import argparse
import sys
import urllib.parse

from common import api_request, get_client, print_json, validate_project_key, validate_status


def list_issues(project: str, status: str, max_results: int) -> dict:
    jira_url, headers = get_client()

    jql = f'project = {project} AND status = "{status}"'
    params = urllib.parse.urlencode({
        "jql": jql,
        "maxResults": max_results,
        "fields": "summary,assignee",
    })
    endpoint = f"{jira_url}/rest/api/3/search/jql?{params}"
    return api_request("GET", endpoint, headers)


def format_result(data: dict) -> dict:
    issues = [
        {
            "key": issue.get("key"),
            "summary": issue.get("fields", {}).get("summary"),
            "assignee": (issue.get("fields", {}).get("assignee") or {}).get("displayName"),
        }
        for issue in data.get("issues", [])
    ]
    return {
        "returned": len(issues),
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="List Jira issues by project and status")
    parser.add_argument("--project", required=True, help="Project key (e.g. DCM)")
    parser.add_argument("--status", required=True, help='Status name (e.g. "In Progress")')
    parser.add_argument("--max-results", type=int, default=50, help="Maximum number of results (default: 50)")
    args = parser.parse_args()

    if args.max_results < 1 or args.max_results > 200:
        print_json({"error": "max-results must be between 1 and 200"})
        sys.exit(1)

    validate_project_key(args.project)
    validate_status(args.status)
    data = list_issues(args.project, args.status, args.max_results)
    print_json(format_result(data))


if __name__ == "__main__":
    main()
