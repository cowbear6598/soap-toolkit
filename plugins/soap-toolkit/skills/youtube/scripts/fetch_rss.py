import argparse
import concurrent.futures
import json
import shutil
import subprocess
import sys
import time


RETRY_SLEEP_SECONDS = 60
PLAYLIST_ITEMS = "1:15"


def fetch_channel(channel_id: str) -> tuple[str, list[str], str | None]:
    """Run yt-dlp for a single channel. Returns (channel_id, json_lines, stderr_or_None)."""
    url = f"https://www.youtube.com/channel/{channel_id}/videos"
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--skip-download",
        "--no-warnings",
        "--playlist-items", PLAYLIST_ITEMS,
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return channel_id, [], result.stderr.strip()
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return channel_id, lines, None


def fetch_channels_parallel(channel_ids: list[str]) -> dict[str, list[str]]:
    """Fetch all channels in parallel, retrying failed ones indefinitely until all succeed."""
    pending = list(channel_ids)
    results: dict[str, list[str]] = {}

    while pending:
        failed: list[str] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(pending)) as executor:
            futures = {executor.submit(fetch_channel, cid): cid for cid in pending}
            for future in concurrent.futures.as_completed(futures):
                channel_id, lines, error = future.result()
                if error is None:
                    results[channel_id] = lines
                else:
                    print(
                        f"Channel {channel_id} failed: {error}",
                        file=sys.stderr,
                    )
                    failed.append(channel_id)

        if failed:
            print(
                f"Retrying failed channels in {RETRY_SLEEP_SECONDS}s: {failed}",
                file=sys.stderr,
            )
            time.sleep(RETRY_SLEEP_SECONDS)
            pending = failed
        else:
            break

    return results


def parse_video(obj: dict) -> dict:
    """Extract relevant fields from a yt-dlp JSON object."""
    video_id: str = obj.get("id", "")
    title: str = obj.get("title", "")
    url: str = obj.get("webpage_url") or obj.get("url", "")

    upload_date: str = obj.get("upload_date", "")
    if len(upload_date) == 8:
        published_at = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    else:
        published_at = upload_date

    raw_desc: str = obj.get("description") or ""
    description: str = raw_desc[:100]

    channel: str = obj.get("channel", "")
    duration: int | None = obj.get("duration")

    return {
        "videoId": video_id,
        "title": title,
        "url": url,
        "publishedAt": published_at,
        "description": description,
        "channel": channel,
        "duration": duration,
    }


def is_short(video: dict) -> bool:
    """Return True if the video should be excluded as a YouTube Short."""
    duration = video.get("duration")
    if duration is not None and duration < 60:
        return True
    title: str = video.get("title", "")
    if "#shorts" in title or "#Shorts" in title:
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch YouTube channel videos via yt-dlp"
    )
    parser.add_argument(
        "--channels",
        nargs="+",
        required=True,
        metavar="CHANNEL_ID",
        help="One or more YouTube channel IDs",
    )
    args = parser.parse_args()

    if shutil.which("yt-dlp") is None:
        print(
            json.dumps(
                {"error": "yt-dlp is not installed or not found in PATH"},
                ensure_ascii=False,
                indent=2,
            )
        )
        sys.exit(1)

    channel_ids: list[str] = args.channels
    channel_data = fetch_channels_parallel(channel_ids)

    all_videos: list[dict] = []
    for channel_id, lines in channel_data.items():
        for line in lines:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(
                    json.dumps(
                        {
                            "error": f"JSON decode error for channel {channel_id}",
                            "detail": {"message": str(e)},
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
                sys.exit(1)
            video = parse_video(obj)
            all_videos.append(video)

    filtered_videos = [v for v in all_videos if not is_short(v)]
    filtered_videos.sort(key=lambda v: v.get("publishedAt", ""))

    result = {
        "total": len(filtered_videos),
        "videos": filtered_videos,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
