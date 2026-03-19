import argparse

from common import api_request, build_adf_doc, get_client, print_json, validate_issue_key, validate_project_key


def build_fields(args: argparse.Namespace) -> dict:
    fields: dict = {
        "project": {"key": args.project},
        "summary": args.summary,
        "issuetype": {"name": args.issue_type},
    }

    if args.description:
        fields["description"] = build_adf_doc(args.description)
    if args.parent:
        fields["parent"] = {"key": args.parent}

    return fields


def create_issue(args: argparse.Namespace) -> dict:
    jira_url, headers = get_client()
    endpoint = f"{jira_url}/rest/api/3/issue"
    return api_request("POST", endpoint, headers, {"fields": build_fields(args)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new Jira issue")
    parser.add_argument("--project", required=True, help="Project key (e.g. PROJ)")
    parser.add_argument("--summary", required=True, help="Issue summary/title")
    parser.add_argument("--description", help="Issue description")
    parser.add_argument("--issue-type", default="Task", help="Issue type (default: Task)")
    parser.add_argument("--parent", help="Parent issue key for creating sub-tasks (e.g. DCM-3923)")
    args = parser.parse_args()

    validate_project_key(args.project)
    if args.parent:
        validate_issue_key(args.parent)

    result = create_issue(args)
    jira_url, _ = get_client()
    issue_key = result.get("key")
    print_json({
        "key": issue_key,
        "id": result.get("id"),
        "url": f"{jira_url}/browse/{issue_key}",
    })


if __name__ == "__main__":
    main()
