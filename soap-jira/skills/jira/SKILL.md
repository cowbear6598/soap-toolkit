---
name: jira
description: "透過 Jira Cloud REST API 操作 Issues。當使用者提到 Jira、ticket、issue、工單、建票、查票、改狀態、留言、或任何與 Jira 專案管理相關的操作時觸發。即使使用者只說「幫我開一張票」「那張票現在什麼狀態」「把它移到 Done」，只要涉及 issue 追蹤，就應該使用這個 skill。"
allowed-tools: Bash(python *), Bash(python3 *)
---

# Jira Cloud Skill

## 環境變數

使用前請確保以下環境變數已設定：

- `JIRA_URL`：Jira Cloud URL（例如 https://your-domain.atlassian.net）
- `JIRA_EMAIL`：Jira 帳號 email
- `JIRA_API_TOKEN`：Jira API Token

透過 Python 腳本操作 Jira Cloud REST API v3。所有腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 腳本一覽

| 腳本 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `list.py` | 列出指定狀態的 Issues | `--project`, `--status` | `--max-results`（預設 50） |
| `get.py` | 取得單張 Issue 詳細資訊 | `--issue` | `--include-subtasks`（加上此參數才會回傳子任務列表） |
| `create.py` | 建立新 Issue | `--project`, `--summary` | `--description`, `--issue-type`（預設 Task）, `--parent` |
| `transition.py` | 切換 Issue 狀態 | `--issue`, `--status` | |
| `comment.py` | 新增評論 | `--issue`, `--comment` | |

## 使用範例

```bash
# 列出 DCM 專案中 In Progress 的 Issues
python <skill-dir>/scripts/list.py --project DCM --status "In Progress"

# 取得單張 Issue
python <skill-dir>/scripts/get.py --issue DCM-1690

# 建立 Bug（帶描述）
python <skill-dir>/scripts/create.py --project DCM --summary "Safari 無法登入" --description "Safari 15+ 點擊登入無反應" --issue-type Bug

# 在父 Issue 下建立子任務
python <skill-dir>/scripts/create.py --project DCM --summary "實作驗證邏輯" --issue-type Subtask --parent DCM-3923

# 切換狀態
python <skill-dir>/scripts/transition.py --issue DCM-1690 --status "In Progress"

# 新增評論
python <skill-dir>/scripts/comment.py --issue DCM-1690 --comment "已確認問題，預計明天修復"
```

## 輸出格式

所有腳本輸出皆為 JSON。錯誤時輸出 `{"error": "...", "detail": {...}}`。

### get.py 回傳欄位

`key`, `type`, `status`, `labels`, `summary`, `description`（純文字）, `subtasks`（子任務列表，每筆含 `key`, `summary`）, `recent_comments`（最近 3 則，含 `author`, `created`, `body`）

### list.py 回傳欄位

`returned`（數量）, `issues`（每筆含 `key`, `summary`, `assignee`）
