import argparse

from common import api_request, get_client, print_json


def get_issue_detail(org: str, headers: dict[str, str], issue_id: str) -> dict:
    url = f"https://sentry.io/api/0/organizations/{org}/issues/{issue_id}/"
    return api_request(url, headers)


def get_latest_event(org: str, headers: dict[str, str], issue_id: str) -> dict:
    url = f"https://sentry.io/api/0/organizations/{org}/issues/{issue_id}/events/latest/"
    return api_request(url, headers)


def extract_stacktrace(event: dict) -> list:
    """Extract exception stacktrace from event entries."""
    exceptions = []
    for entry in event.get("entries", []):
        if entry.get("type") != "exception":
            continue
        for exc in entry.get("data", {}).get("values", []):
            frames = []
            for frame in (exc.get("stacktrace") or {}).get("frames", []):
                frames.append({
                    "filename": frame.get("filename"),
                    "function": frame.get("function"),
                    "lineNo": frame.get("lineNo"),
                    "colNo": frame.get("colNo"),
                    "inApp": frame.get("inApp"),
                })
            exceptions.append({
                "type": exc.get("type"),
                "value": exc.get("value"),
                "frames": frames,
            })
    return exceptions


def format_issue(issue: dict) -> dict:
    assigned = issue.get("assignedTo")
    assigned_name = None
    if assigned:
        assigned_name = assigned.get("name") or assigned.get("email")

    return {
        "id": issue.get("id"),
        "shortId": issue.get("shortId"),
        "title": issue.get("title"),
        "level": issue.get("level"),
        "status": issue.get("status"),
        "count": issue.get("count"),
        "userCount": issue.get("userCount"),
        "firstSeen": issue.get("firstSeen"),
        "lastSeen": issue.get("lastSeen"),
        "assignedTo": assigned_name,
        "permalink": issue.get("permalink"),
    }


def format_event(event: dict) -> dict:
    return {
        "eventID": event.get("eventID"),
        "dateCreated": event.get("dateCreated"),
        "tags": event.get("tags", []),
        "user": event.get("user"),
        "stacktrace": extract_stacktrace(event),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Get Sentry issue detail with latest event stacktrace")
    parser.add_argument("--issue-id", required=True, help="Sentry issue ID")
    args = parser.parse_args()

    org, headers = get_client()

    issue = get_issue_detail(org, headers, args.issue_id)
    event = get_latest_event(org, headers, args.issue_id)

    result = {
        "issue": format_issue(issue),
        "latestEvent": format_event(event),
    }

    print_json(result)


if __name__ == "__main__":
    main()
