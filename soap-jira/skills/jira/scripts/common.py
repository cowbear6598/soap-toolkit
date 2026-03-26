import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid


def get_env() -> tuple[str, str, str]:
    url = os.environ.get("JIRA_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    missing = [name for name, val in [("JIRA_URL", url), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)] if not val]
    if missing:
        print(json.dumps({"error": f"Missing environment variables: {', '.join(missing)}"}))
        sys.exit(1)

    if not url.startswith("https://"):
        print(json.dumps({"error": "JIRA_URL must use HTTPS"}))
        sys.exit(1)

    return url, email, token


def make_headers(email: str, token: str) -> dict[str, str]:
    credentials = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def validate_project_key(key: str) -> None:
    if not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}', key):
        print(json.dumps({"error": f"Invalid project key format: {key[:30]}"}))
        sys.exit(1)


def validate_issue_key(key: str) -> None:
    if not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}-\d{1,7}', key):
        print(json.dumps({"error": f"Invalid issue key format: {key[:30]}"}))
        sys.exit(1)


def validate_status(status: str) -> None:
    if len(status) > 50 or any(c in status for c in ('"', "'", '\\', '\n', '\r')):
        print(json.dumps({"error": "Invalid status value"}))
        sys.exit(1)


def get_client() -> tuple[str, dict[str, str]]:
    jira_url, email, token = get_env()
    return jira_url, make_headers(email, token)


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_adf_doc(text: str) -> dict:
    content = []
    task_items = []

    lines = text.split('\n')

    for line in lines:
        if line.lstrip().startswith('[]'):
            # 提取 [] 後面的文字
            task_text = line.lstrip()[2:].lstrip()
            task_items.append({
                "type": "taskItem",
                "attrs": {
                    "localId": f"item-{uuid.uuid4().hex[:8]}",
                    "state": "TODO"
                },
                "content": [{"type": "text", "text": task_text}]
            })
        else:
            # 如果有累積的 taskItems，先加入 taskList
            if task_items:
                content.append({
                    "type": "taskList",
                    "attrs": {"localId": f"list-{uuid.uuid4().hex[:8]}"},
                    "content": task_items
                })
                task_items = []

            # 將這行作為 paragraph 加入
            if line:
                content.append({
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}]
                })
            else:
                content.append({
                    "type": "paragraph",
                    "content": []
                })

    # 最後如果還有累積的 taskItems，加入 taskList
    if task_items:
        content.append({
            "type": "taskList",
            "attrs": {"localId": f"list-{uuid.uuid4().hex[:8]}"},
            "content": task_items
        })

    return {
        "version": 1,
        "type": "doc",
        "content": content
    }


def _parse_body(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def api_request(method: str, endpoint: str, headers: dict[str, str], body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(endpoint, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return _parse_body(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        detail = _parse_body(raw)
        safe_detail = {
            "errorMessages": detail.get("errorMessages", []),
            "errors": detail.get("errors", {}),
        }
        print(json.dumps({"error": f"HTTP {e.code} {e.reason}", "detail": safe_detail}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Request failed: {e.reason}"}))
        sys.exit(1)
