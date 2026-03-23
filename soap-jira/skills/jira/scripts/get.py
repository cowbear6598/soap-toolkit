import argparse
import urllib.parse

from common import api_request, get_client, print_json, validate_issue_key

FIELDS = "summary,status,issuetype,labels,description,comment,subtasks"


def extract_text(node: dict | None) -> str:
    if not node or not isinstance(node, dict):
        return ''
    text = node.get('text', '')
    for child in node.get('content', []):
        text += extract_text(child)
    return text


def get_issue(issue_key: str) -> dict:
    jira_url, headers = get_client()

    params = urllib.parse.urlencode({"fields": FIELDS})
    endpoint = f"{jira_url}/rest/api/3/issue/{issue_key}?{params}"
    return api_request("GET", endpoint, headers)


def format_issue(data: dict, include_subtasks: bool = False) -> dict:
    fields = data.get("fields", {})
    status = fields.get("status")
    issuetype = fields.get("issuetype")

    comments = fields.get("comment", {}).get("comments", [])
    recent_comments = [
        {
            "author": c.get("author", {}).get("displayName"),
            "created": c.get("created"),
            "body": extract_text(c.get("body")),
        }
        for c in comments[-3:]
    ]

    result = {
        "key": data.get("key"),
        "type": issuetype.get("name") if issuetype else None,
        "status": status.get("name") if status else None,
        "labels": fields.get("labels", []),
        "summary": fields.get("summary"),
        "description": extract_text(fields.get("description")),
        "recent_comments": recent_comments,
    }

    if include_subtasks:
        result["subtasks"] = [
            {"key": s.get("key"), "summary": s.get("fields", {}).get("summary")}
            for s in fields.get("subtasks", [])
        ]

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Get a Jira issue by key")
    parser.add_argument("--issue", required=True, help="Issue key (e.g. DCM-1690)")
    parser.add_argument("--include-subtasks", action="store_true", help="Include subtasks in the response")
    args = parser.parse_args()

    validate_issue_key(args.issue)
    data = get_issue(args.issue)
    print_json(format_issue(data, include_subtasks=args.include_subtasks))


if __name__ == "__main__":
    main()
