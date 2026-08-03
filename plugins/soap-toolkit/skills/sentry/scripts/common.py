from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any
import urllib.error
import urllib.parse
import urllib.request


class SentryError(Exception):
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
    return root / "sentry.json"


def validate_base_url(value: str) -> str:
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
        raise SentryError("Sentry base URL must be a valid HTTPS URL.")
    return url


def validate_organization(value: str) -> str:
    organization = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", organization):
        raise SentryError("Invalid Sentry organization slug.")
    return organization


def validate_short_id(value: str) -> str:
    short_id = value.strip()
    if not short_id or len(short_id) > 128 or any(char.isspace() for char in short_id):
        raise SentryError("Invalid Sentry shortId.")
    return short_id


def load_config() -> dict[str, str]:
    path = config_path()
    if not path.exists():
        raise SentryError(f"Sentry is not configured. Run: python3 {Path(__file__).with_name('setup.py')}")
    if path.is_symlink():
        raise SentryError(f"Refusing to read a symlinked Sentry config: {path}")
    if os.name == "posix" and path.stat().st_mode & 0o077:
        raise SentryError(f"Sentry config permissions are too open. Run: chmod 600 {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SentryError(f"Could not read Sentry config: {exc}") from exc
    if not isinstance(data, dict):
        raise SentryError(f"Sentry config has an invalid structure. Re-run: python3 {Path(__file__).with_name('setup.py')}")

    token = str(data.get("auth_token", "")).strip()
    organization = validate_organization(str(data.get("organization", "")))
    base_url = validate_base_url(str(data.get("base_url", "https://sentry.io")))
    if not token:
        raise SentryError(f"Sentry config is incomplete. Re-run: python3 {Path(__file__).with_name('setup.py')}")
    return {
        "auth_token": token,
        "organization": organization,
        "base_url": base_url,
    }


def api_get(
    config: dict[str, str],
    path: str,
    query: dict[str, str] | None = None,
) -> Any:
    endpoint = f"{config['base_url']}{path}"
    if query:
        endpoint = f"{endpoint}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        endpoint,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {config['auth_token']}",
        },
        method="GET",
    )

    try:
        opener = urllib.request.build_opener(NoRedirect())
        with opener.open(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if 300 <= exc.code < 400:
            message = "Sentry API returned a redirect; refusing to forward credentials."
        elif exc.code in (401, 403):
            message = "Sentry authentication or authorization failed."
        elif exc.code == 404:
            message = "Sentry issue was not found or is not visible to this token."
        elif exc.code == 429:
            message = "Sentry rate limit reached. Try again later."
        else:
            message = f"Sentry request failed with HTTP {exc.code}."
        raise SentryError(message) from exc
    except urllib.error.URLError as exc:
        raise SentryError(f"Sentry request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise SentryError("Sentry returned an invalid JSON response.") from exc


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))
