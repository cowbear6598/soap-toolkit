---
name: list
description: "查詢 Sentry issue 列表。當使用者提到查詢 Sentry issue、sentry issues、sentry list、列出 sentry 錯誤、查看 sentry 問題、或想了解目前有哪些 Sentry 錯誤時觸發。"
allowed-tools: Bash(python3 *), Read
---

# Sentry Issue 列表查詢

透過 Python 腳本查詢 Sentry REST API。腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 環境變數

使用前需設定以下環境變數：

- `SENTRY_AUTH_TOKEN`：Sentry Auth Token
- `SENTRY_ORG`：Sentry Organization slug

## 腳本一覽

| 腳本 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `list_issues.py` | 列出指定專案的 Issues | `--project` | `--status`（預設 unresolved）, `--limit`（預設 25） |

## 使用範例

```bash
# 列出專案未解決的 issues
python3 <skill-dir>/scripts/list_issues.py --project my-project

# 列出已解決的 issues
python3 <skill-dir>/scripts/list_issues.py --project my-project --status resolved

# 限制回傳數量
python3 <skill-dir>/scripts/list_issues.py --project my-project --limit 10

# 列出所有狀態的 issues
python3 <skill-dir>/scripts/list_issues.py --project my-project --status all
```

## 輸出格式

所有輸出皆為 JSON。錯誤時輸出 `{"error": "...", "detail": {...}}`。

### list_issues.py 回傳欄位

`total`（數量）, `issues`（每筆含 `id`, `shortId`, `title`, `level`, `status`, `count`, `userCount`, `firstSeen`, `lastSeen`, `permalink`）

## 注意事項

- **不要在執行腳本前檢查環境變數**（不要 echo、不要 printenv、不要用任何方式確認環境變數是否存在）。直接執行腳本，腳本內部已有完整的錯誤處理，缺少環境變數時會自動回傳 JSON 錯誤訊息。
