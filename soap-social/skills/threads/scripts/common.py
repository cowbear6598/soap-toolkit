import json
import random
import sys
import time
import urllib.error
import urllib.request
from typing import Optional


def random_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> None:
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)


def make_headers() -> dict[str, str]:
    chrome_major = random.randint(128, 134)
    ua = f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_major}.0.0.0 Safari/537.36"
    return {
        "User-Agent": ua,
        "X-IG-App-ID": "238260118697367",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-Ch-Ua": f'"Chromium";v="{chrome_major}", "Google Chrome";v="{chrome_major}", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Upgrade-Insecure-Requests": "1",
    }


def make_googlebot_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
        "Accept": "text/html",
        "Accept-Encoding": "identity",
    }


def _parse_body(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def api_request(url: str, headers: dict[str, str], data: Optional[bytes] = None, method: str = "GET") -> dict:
    if data is not None and method == "GET":
        method = "POST"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return _parse_body(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        detail = _parse_body(raw)
        print(json.dumps({"error": f"HTTP {e.code} {e.reason}", "detail": detail}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Request failed: {e.reason}"}))
        sys.exit(1)


def print_json(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
