import argparse
import sys

from common import api_request, get_client, print_json, validate_issue_key, validate_status


def transition_issue(issue_key: str, status_name: str) -> None:
    jira_url, headers = get_client()

    transitions_endpoint = f"{jira_url}/rest/api/3/issue/{issue_key}/transitions"
    result = api_request("GET", transitions_endpoint, headers)

    transitions = result.get("transitions", [])
    matched = next(
        (t for t in transitions if t.get("name", "").lower() == status_name.lower()),
        None,
    )

    if not matched:
        available = [t.get("name") for t in transitions]
        print_json({"error": f"Transition '{status_name}' not found", "available": available})
        sys.exit(1)

    api_request("POST", transitions_endpoint, headers, {"transition": {"id": matched["id"]}})

    print_json({
        "key": issue_key,
        "url": f"{jira_url}/browse/{issue_key}",
        "transitioned_to": status_name,
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="Transition a Jira issue to a new status")
    parser.add_argument("--issue", required=True, help="Issue key (e.g. PROJ-123)")
    parser.add_argument("--status", required=True, help="Target status name (e.g. 'In Progress', 'Done')")
    args = parser.parse_args()

    validate_issue_key(args.issue)
    validate_status(args.status)
    transition_issue(args.issue, args.status)


if __name__ == "__main__":
    main()
