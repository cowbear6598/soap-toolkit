from __future__ import annotations

import argparse
from typing import Any
import urllib.parse

from common import (
    JiraError,
    api_request,
    issue_url,
    load_config,
    print_json,
    text_to_adf,
    validate_issue_key,
)


def add_comment(issue_key: str, text: str) -> dict[str, Any]:
    comment = text.strip()
    if not comment:
        raise JiraError("Comment cannot be empty.")
    if len(comment) > 32767:
        raise JiraError("Comment is too long.")

    config = load_config()
    encoded_key = urllib.parse.quote(issue_key, safe="")
    result = api_request(
        config,
        "POST",
        f"/rest/api/3/issue/{encoded_key}/comment",
        body={"body": text_to_adf(comment)},
    )
    if not isinstance(result, dict):
        raise JiraError("Jira returned an unexpected comment response.")
    return {
        "key": issue_key,
        "url": issue_url(config, issue_key),
        "commentId": result.get("id"),
        "action": "commented",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Add one comment to a Jira issue")
    parser.add_argument("issue", help="Jira issue key, for example ISSUE-123")
    parser.add_argument("comment", help="Comment text")
    args = parser.parse_args()

    try:
        print_json(add_comment(validate_issue_key(args.issue), args.comment))
    except JiraError as exc:
        print_json({"error": str(exc)})
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
