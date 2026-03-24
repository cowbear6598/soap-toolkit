import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import common

FALLBACK_DOC_ID = "6232751443445612"


def get_user_id(username: str, headers: dict[str, str]) -> str:
    url = f"https://i.instagram.com/api/v1/users/search/?q={urllib.parse.quote(username)}"
    get_headers = {
        "User-Agent": "Barcelona 289.0.0.77.109 Android (33/13; 420dpi; 1080x2400)",
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

    users = data.get("users", [])
    for user in users:
        if user.get("username", "").lower() == username.lower():
            user_id = user.get("pk")
            if user_id:
                return str(user_id)

    print(json.dumps({"error": f"User not found: {username}"}))
    sys.exit(1)


def get_page_tokens(headers: dict[str, str]) -> tuple[str, str, str]:
    """Fetch Threads homepage and extract fb_dtsg, lsd tokens and doc_id from JS bundles."""
    url = "https://www.threads.net/"
    page_headers = {
        "User-Agent": headers["User-Agent"],
        "Cookie": headers["Cookie"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    req = urllib.request.Request(url, headers=page_headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return "", "", FALLBACK_DOC_ID

    # Extract fb_dtsg: long token (20+ chars)
    fb_dtsg = ""
    m = re.search(r'"token":"([^"]{20,})"', html)
    if m:
        fb_dtsg = m.group(1)

    # Extract lsd: shorter token, typically 15-25 chars
    lsd = ""
    m = re.search(r'"LSD"[^"]*"([^"]{10,30})"', html)
    if m:
        lsd = m.group(1)

    # Find JS bundle URLs from the homepage
    bundle_urls = re.findall(
        r'src="(https://static\.cdninstagram\.com/[^"]+\.js[^"]*)"',
        html,
    )

    doc_id = _find_doc_id_in_bundles(bundle_urls, headers)
    if not doc_id:
        doc_id = FALLBACK_DOC_ID

    return fb_dtsg, lsd, doc_id


def _find_doc_id_in_bundles(bundle_urls: list[str], headers: dict[str, str]) -> str:
    """Download JS bundles and search for the ProfileThreadsTab doc_id."""
    fetch_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "*/*",
    }

    for idx, bundle_url in enumerate(bundle_urls):
        if idx > 0:
            common.random_delay()
        try:
            req = urllib.request.Request(bundle_url, headers=fetch_headers, method="GET")
            with urllib.request.urlopen(req, timeout=60) as resp:
                js = resp.read().decode("utf-8", errors="replace")
        except (urllib.error.HTTPError, urllib.error.URLError, Exception):
            continue

        # Look for doc_id near ProfileThreadsTab or mediaData
        # Pattern 1: __d("ProfileThreadsTabQuery_frgmt... followed by an exported number
        m = re.search(
            r'__d\("ProfileThreadsTab[^"]*"[^)]*\).*?e\.exports\s*=\s*"(\d{13,20})"',
            js,
            re.DOTALL,
        )
        if m:
            return m.group(1)

        # Pattern 2: exported number immediately after mediaData mention
        m = re.search(
            r'mediaData[^}]{0,200}e\.exports\s*=\s*"(\d{13,20})"',
            js,
            re.DOTALL,
        )
        if m:
            return m.group(1)

        # Pattern 3: generic exported 13-20 digit number associated with Threads feed
        m = re.search(r'ProfileThreadsFeed[^}]{0,300}e\.exports\s*=\s*"(\d{13,20})"', js, re.DOTALL)
        if m:
            return m.group(1)

    return ""


def fetch_posts(user_id: str, headers: dict[str, str], fb_dtsg: str, lsd: str, doc_id: str) -> list:
    url = "https://www.threads.net/api/graphql"

    variables = json.dumps({
        "userID": user_id,
        "__relay_internal__pv__BarcelonaIsLoggedInrelayprovider": True,
        "__relay_internal__pv__BarcelonaIsThreadContextHeaderEnabledrelayprovider": False,
        "__relay_internal__pv__BarcelonaOptionalCookiesEnabledrelayprovider": True,
        "__relay_internal__pv__BarcelonaIsViewCountEnabledrelayprovider": False,
        "__relay_internal__pv__BarcelonaShouldShowFediverseM075Featuresrelayprovider": False,
    })

    form_data = urllib.parse.urlencode({
        "lsd": lsd,
        "fb_dtsg": fb_dtsg,
        "variables": variables,
        "doc_id": doc_id,
    }).encode()

    post_headers = dict(headers)
    post_headers["X-FB-LSD"] = lsd
    post_headers["Sec-Fetch-Site"] = "same-origin"
    post_headers["Origin"] = "https://www.threads.net"

    result = common.api_request(url, post_headers, data=form_data)
    threads = result.get("data", {}).get("mediaData", {}).get("threads", [])
    return threads


def _extract_text(post: dict) -> str:
    """從 post 中提取文字，優先用 caption，fallback 到 snippet_attachment_info"""
    caption = post.get("caption") or {}
    text = caption.get("text", "") if isinstance(caption, dict) else ""
    if text:
        return text

    # fallback: snippet_attachment_info.text_fragments.fragments[].plaintext
    text_info = post.get("text_post_app_info") or {}
    snippet = text_info.get("snippet_attachment_info") or {}
    fragments_info = snippet.get("text_fragments") or {}
    fragments = fragments_info.get("fragments") or []
    parts = [f.get("plaintext", "") for f in fragments if f.get("plaintext")]
    return "\n".join(parts)


def fetch_replies(post_id: str, session_id: str) -> list[dict]:
    """呼叫 Replies API 取得貼文的回覆串文"""
    url = f"https://i.instagram.com/api/v1/text_feed/{post_id}/replies/"
    headers = {
        "User-Agent": "Barcelona 289.0.0.77.109 Android (33/13; 420dpi; 1080x2400)",
        "X-IG-App-ID": "238260118697367",
        "Cookie": f"sessionid={session_id}",
    }

    common.random_delay()

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            data = json.loads(raw) if raw else {}
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, Exception):
        return []

    reply_threads = data.get("reply_threads") or []
    return reply_threads


def _unix_to_iso(ts) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    except (ValueError, OSError):
        return None


def _extract_media(post: dict) -> list[str]:
    """Extract media URLs (image or video) from a single post object."""
    urls: list[str] = []
    image_versions = post.get("image_versions2")
    if image_versions:
        candidates = image_versions.get("candidates", [])
        if candidates:
            url = candidates[0].get("url")
            if url:
                urls.append(url)

    video_versions = post.get("video_versions")
    if video_versions and not urls:
        url = video_versions[0].get("url") if video_versions else None
        if url:
            urls.append(url)

    return urls


def _get_user_id_from_post(post: dict) -> str | None:
    """Extract the author's user id from a post object."""
    user = post.get("user") or {}
    uid = user.get("pk") or user.get("id")
    return str(uid) if uid is not None else None


def parse_post(thread: dict, session_id: str | None = None) -> dict | None:
    items = thread.get("thread_items", [])
    if not items:
        return None

    post = items[0].get("post", {})
    if not post:
        return None

    post_id = post.get("pk") or post.get("id")
    text = _extract_text(post)
    timestamp = _unix_to_iso(post.get("taken_at"))

    media = _extract_media(post)

    # Determine the main post author for filtering thread chain items
    main_author_id = _get_user_id_from_post(post)

    # Collect texts and post IDs from timeline API items (items[1:])
    seen_post_ids: set[str] = set()
    if post_id is not None:
        seen_post_ids.add(str(post_id))

    extra_texts: list[str] = []
    for item in items[1:]:
        chain_post = item.get("post") or {}
        if not chain_post:
            continue

        # Only merge replies from the same author
        chain_author_id = _get_user_id_from_post(chain_post)
        if main_author_id is None or chain_author_id != main_author_id:
            continue

        chain_pid = chain_post.get("pk") or chain_post.get("id")

        chain_text = _extract_text(chain_post)
        if chain_text:
            extra_texts.append(chain_text)
            # Only mark as seen when text was successfully extracted;
            # otherwise let the Replies API pick up the full content.
            if chain_pid is not None:
                seen_post_ids.add(str(chain_pid))

        # Collect additional media from chain items
        media.extend(_extract_media(chain_post))

    # If thread has replies or multiple items, call Replies API to get full thread
    likes = post.get("like_count") or 0
    text_post_info = post.get("text_post_app_info") or {}
    replies_count = text_post_info.get("direct_reply_count") or 0

    if session_id and post_id:
        try:
            reply_threads = fetch_replies(str(post_id), session_id)
            for rt in reply_threads:
                rt_items = rt.get("thread_items") or []
                for rt_item in rt_items:
                    rt_post = rt_item.get("post") or {}
                    if not rt_post:
                        continue

                    # Only include replies from the same author
                    rt_author_id = _get_user_id_from_post(rt_post)
                    if main_author_id is None or rt_author_id != main_author_id:
                        continue

                    # Deduplicate by post ID
                    rt_pid = rt_post.get("pk") or rt_post.get("id")
                    if rt_pid is not None:
                        rt_pid_str = str(rt_pid)
                        if rt_pid_str in seen_post_ids:
                            continue
                        seen_post_ids.add(rt_pid_str)

                    rt_text = _extract_text(rt_post)
                    if rt_text:
                        extra_texts.append(rt_text)

                    media.extend(_extract_media(rt_post))
        except Exception:
            pass  # Replies API 失敗時靜默跳過

    if extra_texts and text:
        text = "\n\n".join([text] + extra_texts)
    elif extra_texts:
        text = "\n\n".join(extra_texts)
    elif not text:
        text = None

    return {
        "id": str(post_id) if post_id is not None else None,
        "text": text,
        "timestamp": timestamp,
        "media": media,
        "likes": likes,
        "replies": replies_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch latest posts from a Threads user")
    parser.add_argument("--user", required=True, help="Threads username (without @)")
    parser.add_argument("--count", type=int, default=20, help="Number of posts to fetch (default: 20)")
    args = parser.parse_args()

    session_id = common.get_session_id()
    headers = common.make_headers(session_id)

    user_id = get_user_id(args.user, headers)
    common.random_delay()
    fb_dtsg, lsd, doc_id = get_page_tokens(headers)
    common.random_delay()
    threads = fetch_posts(user_id, headers, fb_dtsg, lsd, doc_id)

    posts = []
    for thread in threads:
        post = parse_post(thread, session_id=session_id)
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
