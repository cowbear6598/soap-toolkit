---
name: list
description: "查詢 Sentry issue 列表。當使用者提到查詢 Sentry issue、sentry issues、sentry list、列出 sentry 錯誤、查看 sentry 問題、或想了解目前有哪些 Sentry 錯誤時觸發。"
allowed-tools: Bash(python *), Bash(python3 *), Read
---

# Sentry Issue 列表查詢

透過 Python 腳本查詢 Sentry REST API。腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 環境變數

使用前需設定以下環境變數（`{PROFILE}` 為 profile 名稱的大寫）：

- `SENTRY_AUTH_TOKEN_{PROFILE}`：Sentry Auth Token
- `SENTRY_ORG_{PROFILE}`：Sentry Organization slug

## 腳本一覽

| 腳本 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `list_issues.py` | 列出指定專案的 Issues | `--profile`, `--project` | `--status`（預設 unresolved）, `--limit`（預設 25） |

## 使用範例

```bash
# 列出專案未解決的 issues
python <skill-dir>/scripts/list_issues.py --profile work --project my-project

# 列出已解決的 issues
python <skill-dir>/scripts/list_issues.py --profile work --project my-project --status resolved

# 限制回傳數量
python <skill-dir>/scripts/list_issues.py --profile work --project my-project --limit 10

# 列出所有狀態的 issues
python <skill-dir>/scripts/list_issues.py --profile work --project my-project --status all
```

## 輸出格式

所有輸出皆為 JSON。錯誤時輸出 `{"error": "...", "detail": {...}}`。

### list_issues.py 回傳欄位

`total`（數量）, `issues`（每筆含 `id`, `shortId`, `title`, `level`, `status`, `count`, `userCount`, `firstSeen`, `lastSeen`, `permalink`）
