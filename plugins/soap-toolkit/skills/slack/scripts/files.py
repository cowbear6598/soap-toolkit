#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime, timezone


PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "shared"))

from slack_api import list_channels, load_token, print_json, resolve_channel
from slack_files import list_files, summarize_files


def build_channel_name_map(channels):
    return {channel["id"]: f"#{channel['name']}" for channel in channels}


def normalize_file(file, channel_name_map):
    created = file.get("created")
    created_at = None
    if created:
        created_at = datetime.fromtimestamp(int(created), tz=timezone.utc).isoformat()
    channel_ids = file.get("channels", [])
    return {
        "id": file.get("id"),
        "name": file.get("name"),
        "title": file.get("title"),
        "mimetype": file.get("mimetype"),
        "filetype": file.get("filetype"),
        "pretty_type": file.get("pretty_type"),
        "size": file.get("size"),
        "created": created,
        "created_at": created_at,
        "user": file.get("user"),
        "channels": channel_ids,
        "channel_names": [channel_name_map.get(channel_id, channel_id) for channel_id in channel_ids],
    }


def main():
    parser = argparse.ArgumentParser(description="List Slack files")
    parser.add_argument("--profile", required=True, help="指定使用的 profile")
    parser.add_argument("--channel", help="頻道名稱或 ID")
    parser.add_argument("--all", action="store_true", help="列出 token 可見範圍內所有檔案")
    parser.add_argument("--types", default="all", help="Slack files.list types，預設 all")
    parser.add_argument("--include-non-video", action="store_true", help="包含非影片檔案，預設只列 video/mp4 類檔案")
    parser.add_argument("--older-than-days", type=int, help="只列出 N 天以前的檔案")
    parser.add_argument("--limit", type=int, default=100, help="最多回傳幾筆，預設 100")
    parser.add_argument("--channels", action="store_true", help="列出 bot 可見頻道")
    args = parser.parse_args()

    token = load_token(args.profile)
    channels = list_channels(token)
    if args.channels:
        print_json({"ok": True, "channels": channels})
        return

    if args.channel and args.all:
        print("錯誤：--channel 和 --all 只能擇一使用", file=sys.stderr)
        sys.exit(1)

    channel_id = resolve_channel(token, args.channel) if args.channel else None
    files = list_files(
        token,
        channel_id=channel_id,
        types=args.types,
        older_than_days=args.older_than_days,
        limit=args.limit,
        video_only=not args.include_non_video,
    )
    channel_name_map = build_channel_name_map(channels)
    normalized = [normalize_file(file, channel_name_map) for file in files]
    scope = "all" if args.all or not args.channel else args.channel
    print_json({"ok": True, "scope": scope, "summary": summarize_files(normalized), "files": normalized})


if __name__ == "__main__":
    main()
