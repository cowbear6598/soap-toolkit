---
name: setup
description: "設定 Jira 的認證資訊。當使用者提到要設定 Jira token、setup jira、jira 認證、或想設定 Jira 環境變數時觸發。"
allowed-tools: Bash(python *), Bash(python3 *), Read
---

# Jira 認證設定

透過 Python 腳本產生 helper script，使用者在自己的 terminal 執行，認證資訊不經過對話。

## 工作流程

### Step 1：產生 setup script

執行以下指令：

```bash
python3 <skill-dir>/scripts/generate_setup.py
```

### Step 2：引導使用者

告訴使用者：

1. 開啟自己的 terminal
2. 執行 `bash <生成的 setup_jira.sh 的絕對路徑>`
3. 依照提示輸入 Jira URL、Email、API Token
4. 完成後**重啟 Claude Code** 才會生效

### Step 3：告知取得 API Token 的方式

提供以下資訊：

- **Jira URL**：你的 Jira Cloud 網址，例如 `https://your-domain.atlassian.net`
- **Email**：你登入 Jira 的 email
- **API Token**：前往 https://id.atlassian.com/manage-profile/security/api-tokens → Create API token → 複製

## 注意事項

- API Token 取得頁面：https://id.atlassian.com/manage-profile/security/api-tokens
- URL 必須是 HTTPS
