import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import common


def get_user_id(username: str, headers: dict[str, str]) -> str:
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={urllib.parse.quote(username)}"
    get_headers = {
        "User-Agent": headers["User-Agent"],
        "X-IG-App-ID": headers["X-IG-App-ID"],
        "Cookie": headers["Cookie"],
    }
    req = urllib.request.Request(url, headers=get_headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            print(json.dumps({"error": "Session expired. 請重新從 DevTools 取得 sessionid"}))
            sys.exit(1)
        if e.code == 404:
            print(json.dumps({"error": f"User not found: {username}"}))
            sys.exit(1)
        raw = e.read().decode()
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {"raw": raw}
        print(json.dumps({"error": f"HTTP {e.code} {e.reason}", "detail": detail}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Request failed: {e.reason}"}))
        sys.exit(1)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Failed to parse user info response"}))
        sys.exit(1)

    user = data.get("data", {}).get("user")
    if not user:
        print(json.dumps({"error": f"User not found: {username}"}))
        sys.exit(1)

    user_id = user.get("pk") or user.get("id")
    if not user_id:
        print(json.dumps({"error": f"Unable to retrieve user ID for: {username}"}))
        sys.exit(1)

    return str(user_id)


def fetch_posts(user_id: str, headers: dict[str, str]) -> list:
    url = "https://www.threads.net/api/graphql"

    variables = json.dumps({
        "userID": user_id,
        "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
        "__relay_internal__pv__BarcelonaIsThreadContextHeaderEnabledrelayprovider": False,
    })

    form_data = urllib.parse.urlencode({
        "lsd": "",
        "variables": variables,
        "doc_id": "8515750648528052",
    }).encode()

    post_headers = dict(headers)
    post_headers["X-FB-LSD"] = ""
    post_headers["Sec-Fetch-Site"] = "same-origin"

    result = common.api_request(url, post_headers, data=form_data)
    threads = result.get("data", {}).get("mediaData", {}).get("threads", [])
    return threads


def _unix_to_iso(ts) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, OSError):
        return None


def parse_post(thread: dict) -> dict | None:
    items = thread.get("thread_items", [])
    if not items:
        return None

    post = items[0].get("post", {})
    if not post:
        return None

    post_id = post.get("pk") or post.get("id")
    caption = post.get("caption") or {}
    text = caption.get("text") if isinstance(caption, dict) else None
    timestamp = _unix_to_iso(post.get("taken_at"))

    media = []
    image_versions = post.get("image_versions2")
    if image_versions:
        candidates = image_versions.get("candidates", [])
        if candidates:
            url = candidates[0].get("url")
            if url:
                media.append(url)

    video_versions = post.get("video_versions")
    if video_versions and not media:
        url = video_versions[0].get("url") if video_versions else None
        if url:
            media.append(url)

    likes = post.get("like_count") or 0
    text_post_info = post.get("text_post_app_info") or {}
    replies = text_post_info.get("direct_reply_count") or 0

    return {
        "id": str(post_id) if post_id is not None else None,
        "text": text,
        "timestamp": timestamp,
        "media": media,
        "likes": likes,
        "replies": replies,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch latest posts from a Threads user")
    parser.add_argument("--user", required=True, help="Threads username (without @)")
    parser.add_argument("--count", type=int, default=20, help="Number of posts to fetch (default: 20)")
    args = parser.parse_args()

    session_id = common.get_session_id()
    headers = common.make_headers(session_id)

    user_id = get_user_id(args.user, headers)
    threads = fetch_posts(user_id, headers)

    posts = []
    for thread in threads:
        post = parse_post(thread)
        if post is not None:
            posts.append(post)

    posts = posts[:args.count]

    common.print_json({
        "user": args.user,
        "count": len(posts),
        "posts": posts,
    })


if __name__ == "__main__":
    main()
