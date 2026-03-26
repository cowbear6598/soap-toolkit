import argparse
import sys
import urllib.parse

from common import api_request, get_client, print_json


def resolve_project_id(org: str, headers: dict[str, str], project_slug: str) -> str:
    """Resolve project slug to project ID by querying the projects API."""
    url = f"https://sentry.io/api/0/organizations/{org}/projects/"
    projects = api_request(url, headers)

    if not isinstance(projects, list):
        print_json({"error": "Unexpected response from projects API"})
        sys.exit(1)

    for project in projects:
        if project.get("slug") == project_slug:
            return str(project.get("id"))

    print_json({"error": f"Project '{project_slug}' not found in organization '{org}'"})
    sys.exit(1)


def list_issues(org: str, headers: dict[str, str], project_id: str, status: str, limit: int) -> list:
    query = f"is:{status}" if status != "all" else ""
    params = urllib.parse.urlencode({
        "query": query,
        "project": project_id,
        "limit": limit,
        "sort": "date",
    })
    url = f"https://sentry.io/api/0/organizations/{org}/issues/?{params}"
    return api_request(url, headers)


def format_result(issues: list) -> dict:
    formatted = [
        {
            "id": issue.get("id"),
            "shortId": issue.get("shortId"),
            "title": issue.get("title"),
            "level": issue.get("level"),
            "status": issue.get("status"),
            "count": issue.get("count"),
            "userCount": issue.get("userCount"),
            "firstSeen": issue.get("firstSeen"),
            "lastSeen": issue.get("lastSeen"),
            "permalink": issue.get("permalink"),
        }
        for issue in issues
    ]
    return {
        "total": len(formatted),
        "issues": formatted,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="List Sentry issues by project")
    parser.add_argument("--profile", required=True, help="Profile name (reads SENTRY_AUTH_TOKEN_{PROFILE} and SENTRY_ORG_{PROFILE})")
    parser.add_argument("--project", required=True, help="Sentry project slug")
    parser.add_argument("--status", default="unresolved", choices=["unresolved", "resolved", "ignored", "all"], help="Issue status filter (default: unresolved)")
    parser.add_argument("--limit", type=int, default=25, help="Maximum number of results (default: 25, max: 100)")
    args = parser.parse_args()

    if args.limit < 1 or args.limit > 100:
        print_json({"error": "limit must be between 1 and 100"})
        sys.exit(1)

    org, headers = get_client(args.profile)
    project_id = resolve_project_id(org, headers, args.project)
    issues = list_issues(org, headers, project_id, args.status, args.limit)

    if not isinstance(issues, list):
        print_json({"error": "Unexpected response format from Sentry API"})
        sys.exit(1)

    print_json(format_result(issues))


if __name__ == "__main__":
    main()
