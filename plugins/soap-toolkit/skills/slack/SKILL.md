---
name: slack
description: 設定 Slack Bot Token、發送文字或 Block Kit、回覆 thread、上傳檔案、查詢檔案與清理舊檔案。當使用者要求設定 Slack 認證、發布訊息或檔案、查看檔案用量，或刪除 Slack 舊檔案時使用。
---

# Slack

依使用者目標選用必要能力。草稿或預覽不要發布；永久刪除必須先預覽並確認。所有腳本都位於 `<skill-dir>/scripts/`。

## Setup

Token 只從 `~/.config/soap-toolkit/slack.json` 讀取，不使用 token 環境變數或 shell profile。設定多個 profile 時，名稱會轉成小寫並將 `_` 轉成 `-`；預設 profile 是 `default`。

```bash
python3 <skill-dir>/scripts/setup.py
python3 <skill-dir>/scripts/setup.py --profile notify
```

請使用者在自己的 terminal 執行；腳本隱藏 token、保留其他 profiles、套用 owner-only 權限，完成後立即可用。不要讀取、輸出、回傳或要求使用者貼上 token。只授予需要的 scopes：`chat:write`、`channels:read`、`groups:read`、`files:write`、`files:read`。

## Publish

```bash
python3 <skill-dir>/scripts/send.py --profile default --channel "#general" --message "Hello"
python3 <skill-dir>/scripts/send.py --profile default --channel "#general" --message "fallback" --blocks-json /path/to/blocks.json
python3 <skill-dir>/scripts/upload.py --profile default --channel "#general" --file /path/to/video.mp4
```

Use `--thread-ts` for a reply; upload also accepts `--message` and `--title`. Do not guess the channel, thread, or file. The scripts validate Slack formatting and reject missing, empty, non-file, or larger-than-1GB uploads.

## Inspect

```bash
python3 <skill-dir>/scripts/files.py --profile default --channels
python3 <skill-dir>/scripts/files.py --profile default --channel "#general"
python3 <skill-dir>/scripts/files.py --profile default --all --older-than-days 30
```

Use the smallest requested scope; `--channel` and `--all` are mutually exclusive. Results default to video-like files; add `--include-non-video` only when requested. Slack exposes visible files, not general workspace remaining capacity.

## Clean up

Require an explicit channel or `--all` plus `--older-than-days`. Run the exact selection with `--dry-run`, show identifiable candidates and totals, and delete only after the user confirms that set. Preview again if the conditions or candidates change. Do not broaden scope, include non-video files without explicit direction, or create a schedule.
