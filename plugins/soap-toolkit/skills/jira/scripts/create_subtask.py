from __future__ import annotations

import argparse
from typing import Any
import urllib.parse

from common import (
    JiraError,
    api_get,
    api_request,
    issue_url,
    load_config,
    print_json,
    text_to_adf,
    validate_issue_key,
)


def get_parent_project(config: dict[str, str], parent_key: str) -> str:
    encoded_parent = urllib.parse.quote(parent_key, safe="")
    parent = api_get(
        config,
        f"/rest/api/3/issue/{encoded_parent}",
        {"fields": "project"},
    )
    project = (parent.get("fields") or {}).get("project") if isinstance(parent, dict) else None
    project_key = project.get("key") if isinstance(project, dict) else None
    if not project_key:
        raise JiraError("Jira parent issue response did not include a project key.")
    return str(project_key)


def get_subtask_types(
    config: dict[str, str],
    project_key: str,
) -> list[dict[str, Any]]:
    encoded_project = urllib.parse.quote(project_key, safe="")
    path = f"/rest/api/3/issue/createmeta/{encoded_project}/issuetypes"
    values: list[Any] = []
    start_at = 0
    for _ in range(20):
        result = api_get(
            config,
            path,
            {"maxResults": "100", "startAt": str(start_at)},
        )
        page = result.get("issueTypes", result.get("values")) if isinstance(result, dict) else None
        if not isinstance(page, list):
            raise JiraError("Jira returned an unexpected issue type response.")
        values.extend(page)

        page_start = result.get("startAt", start_at)
        total = result.get("total")
        next_start = page_start + len(page) if isinstance(page_start, int) else start_at + len(page)
        if (
            result.get("isLast") is True
            or not page
            or (isinstance(total, int) and next_start >= total)
            or (total is None and len(page) < 100)
        ):
            break
        if next_start <= start_at:
            raise JiraError("Jira issue type pagination did not advance.")
        start_at = next_start
    else:
        raise JiraError("Jira issue type pagination exceeded the safety limit.")

    return [
        item
        for item in values
        if isinstance(item, dict)
        and (item.get("subtask") is True or item.get("hierarchyLevel") == -1)
    ]


def choose_subtask_type(
    issue_types: list[dict[str, Any]],
    requested: str | None,
) -> dict[str, Any]:
    if requested:
        target = requested.strip().casefold()
        matches = [
            item
            for item in issue_types
            if str(item.get("name", "")).casefold() == target
            or str(item.get("id", "")).casefold() == target
        ]
        if len(matches) == 1:
            return matches[0]
        available = [
            {"id": item.get("id"), "name": item.get("name")}
            for item in issue_types
        ]
        raise JiraError(
            f"Subtask type was not found or is ambiguous: {requested}. "
            f"Available subtask types: {available}"
        )

    if len(issue_types) == 1:
        return issue_types[0]
    available = [
        {"id": item.get("id"), "name": item.get("name")}
        for item in issue_types
    ]
    if not available:
        raise JiraError("This Jira project has no available subtask issue type.")
    raise JiraError(
        "This Jira project has multiple subtask types; provide --issue-type. "
        f"Available subtask types: {available}"
    )


def create_subtask(
    parent_key: str,
    summary: str,
    description: str | None,
    requested_type: str | None,
) -> dict[str, Any]:
    title = summary.strip()
    if not title or len(title) > 255 or any(char in title for char in "\r\n"):
        raise JiraError("Subtask title must be one line between 1 and 255 characters.")
    if description is not None and len(description) > 32767:
        raise JiraError("Subtask description is too long.")

    config = load_config()
    project_key = get_parent_project(config, parent_key)
    issue_type = choose_subtask_type(
        get_subtask_types(config, project_key),
        requested_type,
    )
    issue_type_id = str(issue_type.get("id", ""))
    if not issue_type_id:
        raise JiraError("Selected Jira subtask type has no ID.")

    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "parent": {"key": parent_key},
        "summary": title,
        "issuetype": {"id": issue_type_id},
    }
    if description:
        fields["description"] = text_to_adf(description)

    result = api_request(
        config,
        "POST",
        "/rest/api/3/issue",
        body={"fields": fields},
    )
    if not isinstance(result, dict):
        raise JiraError("Jira returned an unexpected create subtask response.")
    issue_key = str(result.get("key", ""))
    if not issue_key:
        raise JiraError("Jira created a subtask but returned no issue key.")
    return {
        "key": issue_key,
        "id": result.get("id"),
        "url": issue_url(config, issue_key),
        "parent": parent_key,
        "type": issue_type.get("name"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create one Jira subtask")
    parser.add_argument("parent", help="Parent Jira issue key, for example ISSUE-123")
    parser.add_argument("title", help="Subtask title")
    parser.add_argument("--description", help="Optional subtask description")
    parser.add_argument("--issue-type", help="Subtask issue type name or ID")
    args = parser.parse_args()

    try:
        print_json(
            create_subtask(
                validate_issue_key(args.parent),
                args.title,
                args.description,
                args.issue_type,
            )
        )
    except JiraError as exc:
        print_json({"error": str(exc)})
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
