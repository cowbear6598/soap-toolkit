from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import re
from typing import Any
import urllib.error
import urllib.parse
import urllib.request


class JiraError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def config_path() -> Path:
    override = os.environ.get("SOAP_TOOLKIT_CONFIG_DIR")
    root = Path(override).expanduser() if override else Path.home() / ".config" / "soap-toolkit"
    return root / "jira.json"


def validate_url(value: str) -> str:
    url = value.strip().rstrip("/")
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise JiraError("Jira URL must be a valid HTTPS site URL.")
    return url


def validate_issue_key(value: str) -> str:
    issue_key = value.strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,49}-[0-9]{1,12}", issue_key):
        raise JiraError(f"Invalid Jira issue key: {issue_key[:80]}")
    return issue_key.upper()


def load_config() -> dict[str, str]:
    path = config_path()
    if not path.exists():
        raise JiraError(f"Jira is not configured. Run: python3 {Path(__file__).with_name('setup.py')}")
    if path.is_symlink():
        raise JiraError(f"Refusing to read a symlinked Jira config: {path}")
    if os.name == "posix" and path.stat().st_mode & 0o077:
        raise JiraError(f"Jira config permissions are too open. Run: chmod 600 {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise JiraError(f"Could not read Jira config: {exc}") from exc
    if not isinstance(data, dict):
        raise JiraError(f"Jira config has an invalid structure. Re-run: python3 {Path(__file__).with_name('setup.py')}")

    url = validate_url(str(data.get("url", "")))
    email = str(data.get("email", "")).strip()
    token = str(data.get("api_token", "")).strip()
    if not email or not token:
        raise JiraError(f"Jira config is incomplete. Re-run: python3 {Path(__file__).with_name('setup.py')}")
    return {"url": url, "email": email, "api_token": token}


def _error_detail(error: urllib.error.HTTPError) -> str:
    try:
        payload = json.loads(error.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return ""
    if not isinstance(payload, dict):
        return ""

    details = [
        str(message)
        for message in payload.get("errorMessages", [])
        if isinstance(message, str)
    ]
    field_errors = payload.get("errors")
    if isinstance(field_errors, dict):
        details.extend(
            f"{field}: {message}"
            for field, message in field_errors.items()
            if isinstance(message, str)
        )
    return "; ".join(details)[:1000]


def api_request(
    config: dict[str, str],
    method: str,
    path: str,
    query: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    endpoint = f"{config['url']}{path}"
    if query:
        endpoint = f"{endpoint}?{urllib.parse.urlencode(query)}"

    credentials = base64.b64encode(
        f"{config['email']}:{config['api_token']}".encode("utf-8")
    ).decode("ascii")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {credentials}",
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(endpoint, data=data, headers=headers, method=method.upper())

    try:
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        if 300 <= exc.code < 400:
            message = "Jira API returned a redirect; refusing to forward credentials."
        elif exc.code in (401, 403):
            message = "Jira authentication or authorization failed."
        elif exc.code == 404:
            message = "Jira resource was not found or is not visible to this account."
        elif exc.code == 429:
            message = "Jira rate limit reached. Try again later."
        else:
            message = f"Jira request failed with HTTP {exc.code}."
            detail = _error_detail(exc)
            if detail:
                message = f"{message} {detail}"
        raise JiraError(message) from exc
    except urllib.error.URLError as exc:
        raise JiraError(f"Jira request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise JiraError("Jira returned an invalid JSON response.") from exc


def api_get(config: dict[str, str], path: str, query: dict[str, str] | None = None) -> Any:
    return api_request(config, "GET", path, query=query)


def text_to_adf(text: str) -> dict[str, Any]:
    lines = text.splitlines() or [""]
    return {
        "version": 1,
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": line}] if line else [],
            }
            for line in lines
        ],
    }


def issue_url(config: dict[str, str], issue_key: str) -> str:
    encoded_key = urllib.parse.quote(issue_key, safe="")
    return f"{config['url']}/browse/{encoded_key}"


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))
