import argparse
import concurrent.futures
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Optional


YOUTUBE_RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
RETRY_SLEEP_SECONDS = 60

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


def fetch_channel(channel_id: str) -> tuple[str, Optional[bytes], Optional[dict]]:
    """Fetch RSS feed for a single channel. Returns (channel_id, content, error)."""
    url = YOUTUBE_RSS_URL.format(channel_id=channel_id)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, context=ctx) as response:
            return channel_id, response.read(), None
    except urllib.error.HTTPError as e:
        return channel_id, None, {"status": e.code, "reason": e.reason}
    except urllib.error.URLError as e:
        return channel_id, None, {"status": None, "reason": str(e.reason)}


def fetch_channels_parallel(channel_ids: list[str]) -> dict[str, bytes]:
    """Fetch all channels in parallel, retrying failed ones until all succeed."""
    pending = list(channel_ids)
    results: dict[str, bytes] = {}

    while pending:
        failed: list[str] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(fetch_channel, cid): cid for cid in pending}
            for future in concurrent.futures.as_completed(futures):
                channel_id, content, error = future.result()
                if content is not None:
                    results[channel_id] = content
                elif error is not None and error.get("status") in (404, 500):
                    failed.append(channel_id)
                else:
                    # Non-retryable error — surface immediately
                    print(
                        json.dumps(
                            {
                                "error": f"Failed to fetch channel {channel_id}",
                                "detail": error,
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                    )
                    sys.exit(1)

        if failed:
            print(
                f"Channels failed (HTTP 404/500), retrying in {RETRY_SLEEP_SECONDS}s: {failed}",
                file=sys.stderr,
            )
            time.sleep(RETRY_SLEEP_SECONDS)
            pending = failed
        else:
            break

    return results


def parse_entries(channel_id: str, xml_bytes: bytes) -> list[dict]:
    """Parse RSS XML and return list of video entry dicts."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        print(
            json.dumps(
                {
                    "error": f"XML parse error for channel {channel_id}",
                    "detail": {"message": str(e)},
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        sys.exit(1)

    entries: list[dict] = []
    for entry in root.findall("atom:entry", NS):
        video_id_el = entry.find("yt:videoId", NS)
        title_el = entry.find("atom:title", NS)
        link_el = entry.find("atom:link", NS)
        published_el = entry.find("atom:published", NS)
        media_group_el = entry.find("media:group", NS)
        author_el = entry.find("atom:author", NS)

        video_id = video_id_el.text if video_id_el is not None else ""
        title = title_el.text if title_el is not None else ""
        url = link_el.get("href", "") if link_el is not None else ""
        published_at = published_el.text if published_el is not None else ""

        description = ""
        if media_group_el is not None:
            desc_el = media_group_el.find("media:description", NS)
            if desc_el is not None and desc_el.text:
                description = desc_el.text[:100]

        channel = ""
        if author_el is not None:
            name_el = author_el.find("atom:name", NS)
            if name_el is not None:
                channel = name_el.text or ""

        entries.append(
            {
                "videoId": video_id,
                "title": title,
                "url": url,
                "publishedAt": published_at,
                "description": description,
                "channel": channel,
            }
        )

    return entries


def is_short(video: dict) -> bool:
    """Return True if the video is a YouTube Short."""
    title = video.get("title", "")
    url = video.get("url", "")
    description = video.get("description", "")
    return (
        "#shorts" in title
        or "#Shorts" in title
        or "/shorts/" in url
        or "#shorts" in description
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch YouTube RSS feeds for given channel IDs")
    parser.add_argument(
        "--channels",
        nargs="+",
        required=True,
        metavar="CHANNEL_ID",
        help="One or more YouTube channel IDs",
    )
    args = parser.parse_args()

    channel_ids: list[str] = args.channels

    channel_data = fetch_channels_parallel(channel_ids)

    all_videos: list[dict] = []
    for channel_id, xml_bytes in channel_data.items():
        entries = parse_entries(channel_id, xml_bytes)
        all_videos.extend(entries)

    filtered_videos = [v for v in all_videos if not is_short(v)]
    filtered_videos.sort(key=lambda v: v.get("publishedAt", ""))

    result = {
        "total": len(filtered_videos),
        "videos": filtered_videos,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
