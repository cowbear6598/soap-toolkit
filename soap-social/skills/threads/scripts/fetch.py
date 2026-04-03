import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Optional

import common


def get_user_id(username: str) -> str:
    url = f"https://www.threads.com/api/v1/users/web_profile_info/?username={username}"
    headers = common.make_headers()

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
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

    user = data.get("data", {}).get("user") or {}
    user_id = user.get("pk") or user.get("id")
    if user_id:
        return str(user_id)

    print(json.dumps({"error": f"User not found: {username}"}))
    sys.exit(1)


def _extract_bbox_jsons(html: str) -> list[dict]:
    """從 HTML 中找出所有包含 __bbox 的 JSON 物件並解析。"""
    results = []
    # __bbox 資料通常以 {..."__bbox":...} 的形式嵌在 script 標籤內
    # 找所有 require("ScheduledServerJS").handle 或 requireLazy 呼叫中的 JSON 引數
    for m in re.finditer(r'"__bbox"\s*:', html):
        # 往前找到對應的 { 開頭
        start = html.rfind("{", 0, m.start())
        if start == -1:
            continue
        # 往後找對應的 }，用括號計數法
        depth = 0
        end = -1
        for i in range(start, len(html)):
            if html[i] == "{":
                depth += 1
            elif html[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end == -1:
            continue
        try:
            obj = json.loads(html[start:end])
            results.append(obj)
        except json.JSONDecodeError:
            continue
    return results


def _iter_relay_data(bbox_jsons: list[dict]):
    """
    在所有 bbox JSON 中找到 RelayPrefetchedStreamCache 的呼叫，
    逐一 yield 其 result.data dict。

    實際結構：
      bbox.__bbox.require[i] = [
        "RelayPrefetchedStreamCache", "next", [],
        [queryName, {"__bbox": {"result": {"data": {...}}}}]
      ]
    """
    for obj in bbox_jsons:
        bbox = obj.get("__bbox") or {}
        require = bbox.get("require", [])
        for req_item in require:
            if not isinstance(req_item, list) or len(req_item) < 4:
                continue
            module = req_item[0]
            if not isinstance(module, str) or "RelayPrefetchedStreamCache" not in module:
                continue
            args = req_item[3]
            if not isinstance(args, list) or len(args) < 2:
                continue
            inner = args[1]
            if not isinstance(inner, dict):
                continue
            inner_bbox = inner.get("__bbox") or {}
            result = inner_bbox.get("result") or {}
            data = result.get("data")
            if isinstance(data, dict):
                yield data


def _extract_profile_threads(bbox_jsons: list[dict]) -> list[dict]:
    """從所有 relay data 中找到 mediaData.edges（profile threads tab）。"""
    for data in _iter_relay_data(bbox_jsons):
        media_data = data.get("mediaData") or {}
        edges = media_data.get("edges")
        if isinstance(edges, list) and edges:
            return edges
    return []


def fetch_posts_from_ssr(username: str) -> list[dict]:
    """用 Googlebot UA 抓取用戶首頁 SSR HTML，解析出貼文列表。"""
    url = f"https://www.threads.com/@{username}"
    headers = common.make_googlebot_headers()

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(json.dumps({"error": f"User not found: {username}"}))
            sys.exit(1)
        print(json.dumps({"error": f"HTTP {e.code} {e.reason}"}))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": f"Request failed: {e.reason}"}))
        sys.exit(1)

    # 如果頁面是登入頁（非公開 profile），代表用戶不存在或未公開
    if "BarcelonaProfileThreadsTab" not in html:
        print(json.dumps({"error": f"User not found: {username}"}))
        sys.exit(1)

    bbox_jsons = _extract_bbox_jsons(html)
    edges = _extract_profile_threads(bbox_jsons)

    threads = []
    for edge in edges:
        node = edge.get("node")
        if node and isinstance(node, dict):
            threads.append(node)
    return threads


def fetch_thread_chain(username: str, post_code: str) -> list[dict]:
    """用 Googlebot UA 抓取單篇貼文頁，從 SSR __bbox 中提取 thread items。"""
    url = f"https://www.threads.com/@{username}/post/{post_code}"
    headers = common.make_googlebot_headers()

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return []

    bbox_jsons = _extract_bbox_jsons(html)

    # 在所有 relay data 中找 containing_thread.thread_items
    for data in _iter_relay_data(bbox_jsons):
        containing_thread = data.get("containing_thread") or {}
        items = containing_thread.get("thread_items")
        if isinstance(items, list) and items:
            return items

    return []


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


def _unix_to_iso(ts) -> Optional[str]:
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


def _get_user_id_from_post(post: dict) -> Optional[str]:
    """Extract the author's user id from a post object."""
    user = post.get("user") or {}
    uid = user.get("pk") or user.get("id")
    return str(uid) if uid is not None else None


def parse_post(thread: dict) -> Optional[dict]:
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

    main_author_id = _get_user_id_from_post(post)

    seen_post_ids: set[str] = set()
    if post_id is not None:
        seen_post_ids.add(str(post_id))

    extra_texts: list[str] = []
    for item in items[1:]:
        chain_post = item.get("post") or {}
        if not chain_post:
            continue

        chain_author_id = _get_user_id_from_post(chain_post)
        if main_author_id is None or chain_author_id != main_author_id:
            continue

        chain_pid = chain_post.get("pk") or chain_post.get("id")

        chain_text = _extract_text(chain_post)
        if chain_text:
            extra_texts.append(chain_text)
            if chain_pid is not None:
                seen_post_ids.add(str(chain_pid))

        media.extend(_extract_media(chain_post))

    likes = post.get("like_count") or 0
    text_post_info = post.get("text_post_app_info") or {}
    replies_count = text_post_info.get("direct_reply_count") or 0

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


def _get_post_code(post: dict) -> Optional[str]:
    """取得貼文的 shortcode（用於組合 URL）。"""
    return post.get("code")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch latest posts from a Threads user")
    parser.add_argument("--user", required=True, help="Threads username (without @)")
    parser.add_argument("--count", type=int, default=20, help="Number of posts to fetch (default: 20)")
    args = parser.parse_args()

    threads = fetch_posts_from_ssr(args.user)

    posts = []
    for thread in threads:
        items = thread.get("thread_items", [])

        # 如果 SSR 中的 thread_items 只有一個 item，嘗試從貼文頁補充 thread chain
        if len(items) == 1:
            post = items[0].get("post", {}) if items else {}
            post_code = _get_post_code(post)
            if post_code:
                common.random_delay()
                chain_items = fetch_thread_chain(args.user, post_code)
                if len(chain_items) > 1:
                    thread = dict(thread)
                    thread["thread_items"] = chain_items

        parsed = parse_post(thread)
        if parsed is not None:
            posts.append(parsed)

    posts = posts[:args.count]

    common.print_json({
        "user": args.user,
        "count": len(posts),
        "posts": posts,
    })


if __name__ == "__main__":
    main()
