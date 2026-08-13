#!/usr/bin/env python3
import argparse
import os
import sys


PLUGIN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "shared"))

from slack_api import load_token, parse_thread_ts, print_json, resolve_channel, slack_api
from slack_format import load_blocks, validate_slack_format


def main():
    parser = argparse.ArgumentParser(description="Send a Slack message")
    parser.add_argument("--profile", required=True, help="指定使用的 profile")
    parser.add_argument("--channel", required=True, help="頻道名稱或 ID")
    parser.add_argument("--message", required=True, help="訊息內容")
    parser.add_argument("--thread-ts", help="回覆的 thread timestamp 或訊息連結")
    parser.add_argument("--blocks-json", help="Block Kit JSON 檔案路徑")
    args = parser.parse_args()

    blocks = None
    if args.blocks_json:
        try:
            blocks = load_blocks(args.blocks_json)
        except ValueError as e:
            print_json({"ok": False, "error": str(e)}, stream=sys.stderr)
            sys.exit(1)

    errors, warnings = validate_slack_format(message=args.message, blocks=blocks)
    if errors:
        print_json({"ok": False, "error": "format_check_failed", "details": {"errors": errors, "warnings": warnings}}, stream=sys.stderr)
        sys.exit(1)

    token = load_token(args.profile)
    channel_id = resolve_channel(token, args.channel)
    payload = {"channel": channel_id, "text": args.message}
    if args.thread_ts:
        payload["thread_ts"] = parse_thread_ts(args.thread_ts)
    if blocks:
        payload["blocks"] = blocks

    resp = slack_api(token, "chat.postMessage", data=payload)
    if resp.get("ok"):
        print_json({"ok": True, "channel": args.channel, "ts": resp.get("ts", ""), "warnings": warnings})
    else:
        print(f"發送失敗：{resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
