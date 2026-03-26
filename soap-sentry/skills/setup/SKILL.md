---
name: setup
description: "設定 Sentry 的認證資訊。當使用者提到要設定 Sentry token、setup sentry、sentry 認證、或想設定 Sentry 環境變數時觸發。"
allowed-tools: Bash(python *), Bash(python3 *), Read
---

# Sentry 認證設定

透過 Python 腳本產生 helper script，使用者在自己的 terminal 執行，Token 不經過對話。

## 工作流程

### Step 1：產生 setup script

執行以下指令，會在當前目錄產生 `setup_sentry.sh`：

```bash
python3 <skill-dir>/scripts/generate_setup.py
```

### Step 2：引導使用者

告訴使用者：

1. 開啟自己的 terminal
2. 執行 `bash <生成的 setup_sentry.sh 的絕對路徑>`
3. 依照提示輸入 Auth Token、Organization slug
4. 完成後**重啟 Claude Code** 才會生效

### Step 3：告知取得 Token 的方式

提供以下資訊：

- **Auth Token**：登入 https://sentry.io → Settings → Custom Integrations → Create New Integration → Internal Integration → 設定 Permissions（Issue & Event: Read, Project: Read）→ Save → 複製底部 Token
- **Organization slug**：從 URL 取得 `https://sentry.io/organizations/{org-slug}/`

## 注意事項

- Token 需要 `event:read` 和 `project:read` scope
- 如果已有 `SENTRY_AUTH_TOKEN` 或 `SENTRY_ORG` 的設定，會先移除舊的再寫入新的
- 使用者必須重啟 Claude Code 才能讀到新的環境變數
