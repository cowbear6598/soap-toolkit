#!/usr/bin/env python3
import argparse
import os
import sys


PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "shared"))

from slack_api import load_token, parse_thread_ts, print_json, resolve_channel
from slack_files import upload_file
from slack_format import validate_slack_format


def main():
    parser = argparse.ArgumentParser(description="Upload a file to Slack")
    parser.add_argument("--profile", required=True, help="指定使用的 profile")
    parser.add_argument("--channel", required=True, help="頻道名稱或 ID")
    parser.add_argument("--file", required=True, help="檔案路徑")
    parser.add_argument("--message", help="附加說明文字")
    parser.add_argument("--thread-ts", help="回覆的 thread timestamp 或訊息連結")
    parser.add_argument("--title", help="Slack 顯示的檔案標題，預設使用檔名")
    args = parser.parse_args()

    if args.message:
        errors, warnings = validate_slack_format(message=args.message)
        if errors:
            print_json({"ok": False, "error": "format_check_failed", "details": {"errors": errors, "warnings": warnings}}, stream=sys.stderr)
            sys.exit(1)
    else:
        warnings = []

    token = load_token(args.profile)
    channel_id = resolve_channel(token, args.channel)
    file_info = upload_file(
        token,
        channel_id,
        args.file,
        message=args.message,
        thread_ts=parse_thread_ts(args.thread_ts) if args.thread_ts else None,
        title=args.title,
    )
    print_json({"ok": True, "channel": args.channel, "file": file_info, "warnings": warnings})


if __name__ == "__main__":
    main()
