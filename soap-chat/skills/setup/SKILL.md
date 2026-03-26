---
name: setup
description: "設定 Slack 的認證資訊。當使用者提到要設定 Slack token、setup slack、slack 認證、或想設定 Slack Bot Token 時觸發。"
allowed-tools: Bash(python *), Bash(python3 *), Read
---

# Slack 認證設定

透過 Python 腳本產生 helper script，使用者在自己的 terminal 執行，Token 不經過對話。

## 工作流程

### Step 1：產生 setup script

執行以下指令：

```bash
python3 <skill-dir>/scripts/generate_setup.py
```

### Step 2：引導使用者

告訴使用者：

1. 開啟自己的 terminal
2. 執行 `bash <生成的 setup_slack.sh 的絕對路徑>`
3. 依照提示輸入 profile 名稱和 Bot Token
4. 完成後**重啟 Claude Code** 才會生效

### Step 3：告知取得 Bot Token 的方式

提供以下資訊：

- 前往 https://api.slack.com/apps → 選擇你的 App
- OAuth & Permissions → Bot User OAuth Token（xoxb- 開頭）
- 需要的 scopes：`chat:write`、`channels:read`、`files:write`、`files:read`

## 注意事項

- Bot Token 以 `xoxb-` 開頭
- 環境變數名稱的 profile 部分會自動轉大寫
- 如果已有相同 profile 的設定，會先移除舊的再寫入新的
