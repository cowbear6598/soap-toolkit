---
name: detail
description: "查看 Sentry issue 詳情。當使用者提到查看 Sentry issue 詳情、sentry detail、sentry issue 細節、查看 sentry 錯誤詳情、sentry stacktrace、或想了解某個 Sentry 錯誤的詳細資訊時觸發。"
allowed-tools: Bash(python *), Bash(python3 *), Read
---

# Sentry Issue 詳情查詢

透過 Python 腳本查詢 Sentry REST API，取得 issue 詳情和最新 event 的 stacktrace。腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 環境變數

使用前需設定以下環境變數（`{PROFILE}` 為 profile 名稱的大寫）：

- `SENTRY_AUTH_TOKEN_{PROFILE}`：Sentry Auth Token
- `SENTRY_ORG_{PROFILE}`：Sentry Organization slug

## 腳本一覽

| 腳本 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `get_detail.py` | 取得 Issue 詳情含 stacktrace | `--profile`, `--issue-id` | |

## 使用範例

```bash
# 查看 issue 詳情
python <skill-dir>/scripts/get_detail.py --profile work --issue-id 123456789
```

## 輸出格式

所有輸出皆為 JSON。錯誤時輸出 `{"error": "...", "detail": {...}}`。

### get_detail.py 回傳欄位

- `issue`：issue 基本資訊（`id`, `shortId`, `title`, `level`, `status`, `count`, `userCount`, `firstSeen`, `lastSeen`, `assignedTo`, `permalink`）
- `latestEvent`：最新 event 資訊（`eventID`, `dateCreated`, `tags`, `user`, `stacktrace`）
  - `stacktrace` 為陣列，每個 exception 包含 `type`, `value`, `frames`
  - 每個 frame 包含 `filename`, `function`, `lineNo`, `colNo`, `inApp`
