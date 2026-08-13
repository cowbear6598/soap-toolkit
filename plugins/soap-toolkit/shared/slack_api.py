import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def print_json(data, stream=None):
    print(json.dumps(data, ensure_ascii=False), file=stream or sys.stdout)


class SlackConfigError(Exception):
    pass


def config_path():
    override = os.environ.get("SOAP_TOOLKIT_CONFIG_DIR")
    root = Path(override).expanduser() if override else Path.home() / ".config" / "soap-toolkit"
    return root / "slack.json"


def setup_path():
    return Path(__file__).resolve().parent.parent / "skills" / "slack" / "scripts" / "setup.py"


def normalize_profile(value):
    profile = value.strip().lower().replace("_", "-")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", profile):
        raise SlackConfigError("Slack profile must contain only letters, numbers, and hyphens.")
    return profile


def load_config(required=True):
    path = config_path()
    if not path.exists():
        if required:
            raise SlackConfigError(f"Slack is not configured. Run: python3 {setup_path()}")
        return {"profiles": {}}
    if path.is_symlink():
        raise SlackConfigError(f"Refusing to read a symlinked Slack config: {path}")
    if os.name == "posix" and path.stat().st_mode & 0o077:
        raise SlackConfigError(f"Slack config permissions are too open. Run: chmod 600 {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SlackConfigError(f"Could not read Slack config: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("profiles"), dict):
        raise SlackConfigError(f"Slack config must contain a profiles object. Re-run: python3 {setup_path()}")
    return data


def load_token(profile):
    try:
        normalized = normalize_profile(profile)
        config = load_config()
        entry = config["profiles"].get(normalized)
        token = entry.get("bot_token", "").strip() if isinstance(entry, dict) else ""
        if not token:
            raise SlackConfigError(
                f"Slack profile '{normalized}' is not configured in {config_path()}. Run: python3 {setup_path()}"
            )
        return token
    except SlackConfigError as exc:
        print_json({"error": str(exc)}, stream=sys.stderr)
        sys.exit(1)


def slack_api(token, method, data=None, params=None, content_type="json"):
    url = f"https://slack.com/api/{method}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        if content_type == "form":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            body = urllib.parse.urlencode(data).encode("utf-8")
        else:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        fail(f"HTTP {e.code}: {body}")


def resolve_channel(token, channel_name):
    if re.match(r"^[A-Z0-9]+$", channel_name):
        return channel_name

    name = channel_name.lstrip("#")
    cursor = None

    while True:
        params = {"types": "public_channel,private_channel", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        resp = slack_api(token, "conversations.list", params=params)
        if not resp.get("ok"):
            fail(f"錯誤：無法取得頻道列表 — {resp.get('error', 'unknown')}")

        for ch in resp.get("channels", []):
            if ch["name"] == name:
                return ch["id"]

        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    fail(f"錯誤：找不到頻道 #{name}")


def parse_thread_ts(value):
    match = re.search(r"/p(\d{16})$", value)
    if match:
        raw = match.group(1)
        return f"{raw[:10]}.{raw[10:]}"
    return value


def list_channels(token):
    cursor = None
    channels = []

    while True:
        params = {"types": "public_channel,private_channel", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        resp = slack_api(token, "conversations.list", params=params)
        if not resp.get("ok"):
            fail(f"錯誤：{resp.get('error', 'unknown')}")

        for ch in resp.get("channels", []):
            channels.append(
                {
                    "id": ch["id"],
                    "name": ch["name"],
                    "is_member": bool(ch.get("is_member")),
                }
            )

        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return sorted(channels, key=lambda ch: ch["name"])
