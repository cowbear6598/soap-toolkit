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
    validate_issue_key,
)


def transition_label(transition: dict[str, Any]) -> dict[str, Any]:
    target = transition.get("to") or {}
    return {
        "transition": transition.get("name"),
        "status": target.get("name"),
    }


def choose_transition(
    transitions: list[dict[str, Any]],
    requested: str,
) -> dict[str, Any]:
    target = requested.casefold()
    exact_name = [
        item
        for item in transitions
        if str(item.get("name", "")).casefold() == target
    ]
    status_matches = [
        item
        for item in transitions
        if str((item.get("to") or {}).get("name", "")).casefold() == target
    ]
    matches = []
    for item in exact_name + status_matches:
        if item not in matches:
            matches.append(item)
    if len(matches) == 1:
        return matches[0]

    available = [transition_label(item) for item in transitions]
    if matches:
        raise JiraError(
            f"Transition target is ambiguous: {requested}. "
            f"Available transitions: {available}"
        )
    raise JiraError(
        f"Transition or target status was not found: {requested}. "
        f"Available transitions: {available}"
    )


def transition_issue(issue_key: str, requested: str) -> dict[str, Any]:
    target = requested.strip()
    if not target or len(target) > 100 or any(char in target for char in "\r\n"):
        raise JiraError("Invalid transition or status name.")

    config = load_config()
    encoded_key = urllib.parse.quote(issue_key, safe="")
    path = f"/rest/api/3/issue/{encoded_key}/transitions"
    result = api_get(config, path)
    transitions = result.get("transitions") if isinstance(result, dict) else None
    if not isinstance(transitions, list):
        raise JiraError("Jira returned an unexpected transitions response.")

    selected = choose_transition(
        [item for item in transitions if isinstance(item, dict)],
        target,
    )
    transition_id = str(selected.get("id", ""))
    if not transition_id:
        raise JiraError("Selected Jira transition has no ID.")

    api_request(
        config,
        "POST",
        path,
        body={"transition": {"id": transition_id}},
    )
    target_status = (selected.get("to") or {}).get("name")
    return {
        "key": issue_key,
        "url": issue_url(config, issue_key),
        "transition": selected.get("name"),
        "status": target_status,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Transition one Jira issue")
    parser.add_argument("issue", help="Jira issue key, for example ISSUE-123")
    parser.add_argument("target", help="Transition name or target status")
    args = parser.parse_args()

    try:
        print_json(transition_issue(validate_issue_key(args.issue), args.target))
    except JiraError as exc:
        print_json({"error": str(exc)})
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
