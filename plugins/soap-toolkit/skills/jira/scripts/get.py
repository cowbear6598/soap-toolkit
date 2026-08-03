from __future__ import annotations

import argparse
from datetime import datetime, timezone
import re
from typing import Any
import urllib.parse

from common import JiraError, api_get, load_config, print_json, validate_issue_key


def render_adf(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(render_adf(child) for child in node)
    if not isinstance(node, dict):
        return ""

    node_type = node.get("type")
    if node_type == "text":
        return str(node.get("text", ""))
    if node_type == "hardBreak":
        return "\n"

    attrs = node.get("attrs") or {}
    if node_type in {"mention", "status"}:
        return str(attrs.get("text", ""))
    if node_type == "emoji":
        return str(attrs.get("text") or attrs.get("shortName") or "")
    if node_type in {"inlineCard", "blockCard"}:
        return str(attrs.get("url", ""))
    if node_type == "date":
        timestamp = attrs.get("timestamp")
        try:
            return datetime.fromtimestamp(
                int(timestamp) / 1000,
                tz=timezone.utc,
            ).date().isoformat()
        except (TypeError, ValueError, OverflowError):
            return str(timestamp or "")

    children = node.get("content", [])
    if node_type == "orderedList":
        rendered = []
        start = int((node.get("attrs") or {}).get("order", 1))
        for index, child in enumerate(children, start=start):
            child_content = (
                child.get("content", [])
                if isinstance(child, dict) and child.get("type") == "listItem"
                else child
            )
            rendered.append(f"{index}. {render_adf(child_content).strip()}\n")
        return "".join(rendered)
    if node_type in {"listItem", "taskItem"}:
        return f"- {render_adf(children).strip()}\n"
    if node_type == "tableCell":
        return f"{render_adf(children).strip()}\t"
    if node_type == "tableRow":
        return f"{render_adf(children).rstrip()}\n"

    text = render_adf(children)
    if node_type in {
        "paragraph",
        "heading",
        "blockquote",
        "codeBlock",
        "panel",
        "mediaSingle",
        "rule",
    }:
        return f"{text.rstrip()}\n"
    return text


def description_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    text = render_adf(value)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_issue(issue_key: str) -> dict[str, Any]:
    config = load_config()
    encoded_key = urllib.parse.quote(issue_key, safe="")
    data = api_get(
        config,
        f"/rest/api/3/issue/{encoded_key}",
        {"fields": "summary,description"},
    )
    if not isinstance(data, dict):
        raise JiraError("Jira returned an unexpected issue response.")

    fields = data.get("fields") or {}
    canonical_key = str(data.get("key") or issue_key)
    return {
        "key": canonical_key,
        "url": f"{config['url']}/browse/{urllib.parse.quote(canonical_key, safe='')}",
        "title": fields.get("summary"),
        "description": description_text(fields.get("description")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Get a Jira issue title and description")
    parser.add_argument("issue", help="Jira issue key, for example ISSUE-123")
    args = parser.parse_args()

    try:
        print_json(get_issue(validate_issue_key(args.issue)))
    except JiraError as exc:
        print_json({"error": str(exc)})
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
