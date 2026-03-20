---
name: slack
description: "發送訊息到 Slack 頻道。當使用者提到「發到 Slack」「傳到 Slack」「send to Slack」「通知 Slack」「Slack 發訊息」或想把任何內容傳送到 Slack 頻道時觸發。"
---

所有操作都透過 `scripts/slack-chat.py` 執行，腳本路徑相對於此 SKILL.md 所在目錄。

支援多個 Slack Bot，透過 `--bot` 指定要用哪個。`--bot` 為必要參數，不指定會報錯並列出可用的 bot。Bot 設定在 `skills/config.json`。

## 指令

### 列出已設定的 Bot

```bash
python3 scripts/slack-chat.py bots
```

### 列出可用頻道

```bash
python3 scripts/slack-chat.py channels --bot BOT名稱
```

會顯示 Bot 可見的所有頻道，標示 ✓ 表示 Bot 已加入。如果使用者不確定要發到哪個頻道，先跑這個讓他選。

### 發送文字訊息

```bash
python3 scripts/slack-chat.py send --channel "#頻道名稱" --message "訊息內容" --bot BOT名稱
```

### 發送 Block Kit 排版訊息

當內容有結構（標題、列表、多段落）時，用 Block Kit 排版效果更好。先把 blocks JSON 寫成檔案，再傳入：

```bash
python3 scripts/slack-chat.py send --channel "#頻道名稱" --message "fallback 純文字" --blocks-json /tmp/blocks.json --bot BOT名稱
```

Block Kit JSON 範例（寫入 `/tmp/blocks.json`）：

```json
[
  {
    "type": "header",
    "text": { "type": "plain_text", "text": "標題" }
  },
  {
    "type": "section",
    "text": { "type": "mrkdwn", "text": "*粗體* _斜體_\n• 項目一\n• 項目二" }
  },
  {
    "type": "divider"
  },
  {
    "type": "context",
    "elements": [
      { "type": "mrkdwn", "text": "備註文字" }
    ]
  }
]
```

根據使用者內容自動判斷：
- 純文字、短訊息 → 直接用 `--message` 發送
- 有結構的內容（標題、列表、多段落）→ 產生 blocks JSON 再發送

### 回覆 Thread

加上 `--thread-ts` 參數，支援直接填 timestamp 或貼 Slack 訊息連結：

```bash
python3 scripts/slack-chat.py send --channel "#頻道" --message "回覆內容" --thread-ts "1234567890.123456"
python3 scripts/slack-chat.py send --channel "#頻道" --message "回覆內容" --thread-ts "https://xxx.slack.com/archives/C01234/p1234567890123456"
```

### 上傳檔案/圖片

```bash
python3 scripts/slack-chat.py upload --channel "#頻道" --file /path/to/file --message "附加說明（可選）" --bot BOT名稱
```

同樣支援 `--thread-ts` 回覆到特定 thread。

## 錯誤處理

腳本會自動檢查 API 回傳並顯示錯誤訊息。常見錯誤：
- `not_in_channel` → Bot 尚未加入該頻道，提示使用者在 Slack 中邀請 Bot
- `channel_not_found` → 頻道名稱/ID 錯誤，可以先跑 `channels` 確認
- `invalid_auth` → Token 無效，請使用者檢查 `config.json`
- `missing_scope` → Token 缺少權限（需要 `chat:write`、`files:write`、`channels:read`）
