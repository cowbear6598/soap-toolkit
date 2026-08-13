#!/usr/bin/env python3
import argparse
import os
import sys


PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "shared"))

from slack_api import load_token, print_json, resolve_channel
from slack_files import delete_file, list_files, summarize_files


def main():
    parser = argparse.ArgumentParser(description="Delete old Slack files")
    parser.add_argument("--profile", required=True, help="指定使用的 profile")
    parser.add_argument("--channel", help="頻道名稱或 ID")
    parser.add_argument("--all", action="store_true", help="清理 token 可見範圍內所有符合條件的檔案")
    parser.add_argument("--older-than-days", type=int, required=True, help="刪除 N 天以前的檔案")
    parser.add_argument("--types", default="all", help="Slack files.list types，預設 all")
    parser.add_argument("--include-non-video", action="store_true", help="包含非影片檔案，預設只刪 video/mp4 類檔案")
    parser.add_argument("--limit", type=int, default=100, help="最多處理幾筆，預設 100")
    parser.add_argument("--dry-run", action="store_true", help="只列出將刪除的檔案，不刪除")
    args = parser.parse_args()

    if bool(args.channel) == bool(args.all):
        print("錯誤：請指定 --channel 或 --all，且只能擇一使用", file=sys.stderr)
        sys.exit(1)

    token = load_token(args.profile)
    channel_id = resolve_channel(token, args.channel) if args.channel else None
    files = list_files(
        token,
        channel_id=channel_id,
        types=args.types,
        older_than_days=args.older_than_days,
        limit=args.limit,
        video_only=not args.include_non_video,
    )

    if args.dry_run:
        print_json({"ok": True, "dry_run": True, "scope": args.channel or "all", "summary": summarize_files(files), "files": files})
        return

    deleted = []
    failed = []
    for file in files:
        file_id = file.get("id")
        if not file_id:
            continue
        if delete_file(token, file_id):
            deleted.append(file_id)
        else:
            failed.append(file_id)

    print_json(
        {
            "ok": not failed,
            "dry_run": False,
            "scope": args.channel or "all",
            "matched": summarize_files(files),
            "deleted": deleted,
            "failed": failed,
        }
    )
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
