---
name: slack
description: "發送訊息到 Slack。當使用者提到「發到 Slack」「傳到 Slack」「send to Slack」「通知 Slack」「Slack 發訊息」或想傳送內容到 Slack 頻道時觸發。"
allowed-tools: Bash(python3 *), Read
---

# Slack Messaging

透過 Python 腳本操作 Slack API。腳本位於 `<skill-dir>/scripts/`。

## 環境變數

使用前需設定以下環境變數（`{PROFILE}` 為 profile 名稱的大寫）：

- `SLACK_BOT_TOKEN_{PROFILE}`：Slack Bot Token（xoxb- 開頭）

## 腳本用法

| 指令 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `channels` | 列出頻道 | `--profile` | |
| `send` | 發送文字訊息 | `--profile`, `--channel`, `--message` | `--blocks-json`, `--thread-ts` |
| `upload` | 上傳檔案 | `--profile`, `--channel`, `--file` | `--message`, `--thread-ts` |

## 使用範例

```bash
# 列出頻道
python3 <skill-dir>/scripts/slack-chat.py channels --profile default

# 發送文字訊息
python3 <skill-dir>/scripts/slack-chat.py send --profile default --channel "#general" --message "Hello"

# 發送 Block Kit 格式訊息
python3 <skill-dir>/scripts/slack-chat.py send --profile default --channel "#general" --message "fallback text" --blocks-json /path/to/blocks.json

# 上傳檔案
python3 <skill-dir>/scripts/slack-chat.py upload --profile default --channel "#general" --file /path/to/image.png

# 回覆串（thread）
python3 <skill-dir>/scripts/slack-chat.py send --profile default --channel "#general" --message "reply" --thread-ts 1234567890.123456
```

## 輸出格式

所有成功輸出皆為 JSON，失敗時錯誤訊息輸出到 stderr，exit code 為 1。

**send 成功範例：**
```json
{"ok": true, "channel": "#general", "ts": "1234567890.123456"}
```

**upload 成功範例：**
```json
{"ok": true, "channel": "#general", "file": {"id": "F0123ABC", "name": "image.png"}}
```

**失敗範例：** 錯誤訊息輸出到 stderr，exit code 1。

回傳的 `ts` 可用於後續 `--thread-ts` 參數，用來回覆該訊息（建立 thread）。

## 注意事項

- `--channel` 可以用頻道名稱（如 `#general`）或頻道 ID（如 `C01234ABCDE`）
- `--thread-ts` 支援 timestamp 格式或 Slack 訊息連結
- `--blocks-json` 指向包含 Block Kit JSON 的檔案路徑
- **不要在執行腳本前檢查環境變數**（不要 echo、不要 printenv、不要用任何方式確認環境變數是否存在）。直接執行腳本，腳本內部已有完整的錯誤處理，缺少環境變數時會自動回傳 JSON 錯誤訊息。
