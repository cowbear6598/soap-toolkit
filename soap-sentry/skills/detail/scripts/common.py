import json
import os
import sys
import urllib.error
import urllib.request


def get_env() -> tuple[str, str]:
    token = os.environ.get("SENTRY_AUTH_TOKEN", "")
    org = os.environ.get("SENTRY_ORG", "")

    missing = [name for name, val in [("SENTRY_AUTH_TOKEN", token), ("SENTRY_ORG", org)] if not val]
    if missing:
        print(json.dumps({"error": f"Missing environment variables: {', '.join(missing)}. Please set them in your shell profile."}))
        sys.exit(1)

    return token, org


def make_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_client() -> tuple[str, dict[str, str]]:
    token, org = get_env()
    return org, make_headers(token)


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _parse_body(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def api_request(url: str, headers: dict[str, str]) -> dict | list:
    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return _parse_body(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        detail = _parse_body(raw)
        if e.code in (401, 403):
            print(json.dumps({"error": f"Authentication failed (HTTP {e.code}). Please check your token.", "detail": detail}))
        elif e.code == 404:
            print(json.dumps({"error": "Not found (HTTP 404). Please check the organization, project, or issue ID.", "detail": detail}))
        elif e.code == 429:
            print(json.dumps({"error": "Rate limited (HTTP 429). Please wait a moment and try again.", "detail": detail}))
        else:
            print(json.dumps({"error": f"HTTP {e.code} {e.reason}", "detail": detail}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Request failed: {e.reason}"}))
        sys.exit(1)
