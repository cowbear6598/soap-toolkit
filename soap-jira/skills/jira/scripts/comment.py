import argparse
import sys

from common import api_request, build_adf_doc, get_client, print_json, validate_issue_key


def add_comment(issue_key: str, comment_text: str) -> None:
    jira_url, headers = get_client()

    endpoint = f"{jira_url}/rest/api/3/issue/{issue_key}/comment"
    body = {"body": build_adf_doc(comment_text)}
    api_request("POST", endpoint, headers, body)

    print_json({
        "key": issue_key,
        "url": f"{jira_url}/browse/{issue_key}",
        "action": "comment added",
    })


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a comment to a Jira issue")
    parser.add_argument("--issue", required=True, help="Issue key (e.g. PROJ-123)")
    parser.add_argument("--comment", required=True, help="Comment text to add")
    args = parser.parse_args()

    validate_issue_key(args.issue)
    if len(args.comment) > 10000:
        print_json({"error": "Comment too long (max 10000 characters)"})
        sys.exit(1)
    add_comment(args.issue, args.comment)


if __name__ == "__main__":
    main()
