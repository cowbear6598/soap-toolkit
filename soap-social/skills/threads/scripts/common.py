import json
import os
import sys
import urllib.error
import urllib.request


def _load_dotenv() -> None:
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # 環境變數優先，.env 只補齊尚未設定的值
            if key and key not in os.environ:
                os.environ[key] = value


def get_session_id() -> str:
    _load_dotenv()
    session_id = os.environ.get("THREADS_SESSION_ID", "")
    if not session_id:
        print(json.dumps({"error": "Missing environment variable: THREADS_SESSION_ID"}))
        sys.exit(1)
    return session_id


def make_headers(session_id: str) -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Cookie": f"sessionid={session_id}",
        "X-IG-App-ID": "238260118697367",
        "Content-Type": "application/x-www-form-urlencoded",
    }


def _parse_body(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def api_request(url: str, headers: dict[str, str], data: bytes | None = None) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return _parse_body(raw) if raw else {}
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(json.dumps({"error": "Session expired. 請重新從 DevTools 取得 sessionid"}))
            sys.exit(1)
        raw = e.read().decode()
        detail = _parse_body(raw)
        print(json.dumps({"error": f"HTTP {e.code} {e.reason}", "detail": detail}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Request failed: {e.reason}"}))
        sys.exit(1)


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
