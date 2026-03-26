#!/usr/bin/env python3
"""
soap-chat Slack script — 發送訊息、上傳檔案到 Slack 頻道。

Usage:
  python3 slack-chat.py send --profile PROFILE --channel CHANNEL --message MESSAGE [--thread-ts TS] [--blocks-json PATH]
  python3 slack-chat.py upload --profile PROFILE --channel CHANNEL --file PATH [--message MESSAGE] [--thread-ts TS]
  python3 slack-chat.py channels --profile PROFILE
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.parse
import urllib.error


def load_token(profile: str) -> str:
    suffix = profile.upper().replace("-", "_")
    key = f"SLACK_BOT_TOKEN_{suffix}"
    token = os.environ.get(key, "")
    if not token:
        print(json.dumps({"error": f"Missing environment variable: {key}. Please set it in your shell profile."}))
        sys.exit(1)
    return token


def slack_api(token, method, data=None, files=None):
    """呼叫 Slack API，回傳 JSON dict"""
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {token}"}

    if files:
        # multipart upload — 用 urllib 不方便，改用 curl
        import subprocess
        cmd = ["curl", "-s", "-X", "POST", url, "-H", f"Authorization: Bearer {token}"]
        for key, val in (data or {}).items():
            cmd += ["-F", f"{key}={val}"]
        for key, path in files.items():
            cmd += ["-F", f"{key}=@{path}"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)

    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def resolve_channel(token, channel_name):
    """頻道名稱 → channel ID。如果已經是 ID 則直接回傳。"""
    if re.match(r'^[A-Z0-9]+$', channel_name):
        return channel_name

    name = channel_name.lstrip("#")
    cursor = None

    while True:
        params = "types=public_channel,private_channel&limit=200"
        if cursor:
            params += f"&cursor={urllib.parse.quote(cursor)}"
        resp = slack_api(token, f"conversations.list?{params}")
        if not resp.get("ok"):
            print(f"錯誤：無法取得頻道列表 — {resp.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)

        for ch in resp.get("channels", []):
            if ch["name"] == name:
                return ch["id"]

        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    print(f"錯誤：找不到頻道 #{name}", file=sys.stderr)
    sys.exit(1)


def parse_thread_ts(value):
    """支援直接 ts 或 Slack 訊息連結，回傳 thread_ts 字串。"""
    match = re.search(r'/p(\d{16})$', value)
    if match:
        raw = match.group(1)
        return f"{raw[:10]}.{raw[10:]}"
    return value


def cmd_channels(token):
    """列出 Bot 可見的所有頻道"""
    cursor = None
    channels = []

    while True:
        params = "types=public_channel,private_channel&limit=200"
        if cursor:
            params += f"&cursor={urllib.parse.quote(cursor)}"
        resp = slack_api(token, f"conversations.list?{params}")
        if not resp.get("ok"):
            print(f"錯誤：{resp.get('error', 'unknown')}", file=sys.stderr)
            sys.exit(1)

        for ch in resp.get("channels", []):
            marker = "✓" if ch.get("is_member") else " "
            channels.append((marker, ch["name"], ch["id"]))

        cursor = resp.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    if not channels:
        print("沒有找到任何頻道")
        return

    print(f"{'':2} {'頻道名稱':<30} {'ID'}")
    print("-" * 50)
    for marker, name, cid in sorted(channels, key=lambda x: x[1]):
        print(f"[{marker}] #{name:<28} {cid}")
    print(f"\n共 {len(channels)} 個頻道（✓ = Bot 已加入）")


def cmd_send(token, args):
    """發送文字或 Block Kit 訊息"""
    channel_id = resolve_channel(token, args.channel)

    payload = {"channel": channel_id, "text": args.message}

    if args.thread_ts:
        payload["thread_ts"] = parse_thread_ts(args.thread_ts)

    if args.blocks_json:
        with open(args.blocks_json) as f:
            payload["blocks"] = json.load(f)

    resp = slack_api(token, "chat.postMessage", data=payload)

    if resp.get("ok"):
        ts = resp.get("ts", "")
        print(f"已發送到 #{args.channel}（ts: {ts}）")
    else:
        print(f"發送失敗：{resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


def cmd_upload(token, args):
    """上傳檔案到頻道（v2 流程）"""
    channel_id = resolve_channel(token, args.channel)
    file_path = args.file

    if not os.path.exists(file_path):
        print(f"錯誤：檔案不存在 — {file_path}", file=sys.stderr)
        sys.exit(1)

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    # Step 1: 取得上傳 URL
    params = f"filename={urllib.parse.quote(file_name)}&length={file_size}"
    resp = slack_api(token, f"files.getUploadURLExternal?{params}")
    if not resp.get("ok"):
        print(f"取得上傳 URL 失敗：{resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    upload_url = resp["upload_url"]
    file_id = resp["file_id"]

    # Step 2: 上傳檔案
    import subprocess
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", upload_url, "-F", f"file=@{file_path}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"上傳失敗：{result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Step 3: 完成上傳
    complete_data = {
        "files": [{"id": file_id, "title": file_name}],
        "channel_id": channel_id,
    }
    if args.message:
        complete_data["initial_comment"] = args.message
    if args.thread_ts:
        complete_data["thread_ts"] = parse_thread_ts(args.thread_ts)

    resp = slack_api(token, "files.completeUploadExternal", data=complete_data)
    if resp.get("ok"):
        print(f"已上傳 {file_name} 到 #{args.channel}")
    else:
        print(f"完成上傳失敗：{resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="soap-chat Slack CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # channels
    p_channels = sub.add_parser("channels", help="列出可用頻道")
    p_channels.add_argument("--profile", required=True, help="指定使用的 profile")

    # send
    p_send = sub.add_parser("send", help="發送訊息")
    p_send.add_argument("--profile", required=True, help="指定使用的 profile")
    p_send.add_argument("--channel", required=True, help="頻道名稱或 ID")
    p_send.add_argument("--message", required=True, help="訊息內容")
    p_send.add_argument("--thread-ts", help="回覆的 thread timestamp 或訊息連結")
    p_send.add_argument("--blocks-json", help="Block Kit JSON 檔案路徑")

    # upload
    p_upload = sub.add_parser("upload", help="上傳檔案")
    p_upload.add_argument("--profile", required=True, help="指定使用的 profile")
    p_upload.add_argument("--channel", required=True, help="頻道名稱或 ID")
    p_upload.add_argument("--file", required=True, help="檔案路徑")
    p_upload.add_argument("--message", help="附加說明文字")
    p_upload.add_argument("--thread-ts", help="回覆的 thread timestamp 或訊息連結")

    args = parser.parse_args()

    token = load_token(args.profile)
    if args.command == "channels":
        cmd_channels(token)
    elif args.command == "send":
        cmd_send(token, args)
    elif args.command == "upload":
        cmd_upload(token, args)


if __name__ == "__main__":
    main()
