---
name: threads-setup
description: "設定 Threads 的認證資訊。當使用者提到要設定 Threads session、設定 Threads token、setup threads、或提供 Threads session ID 要求存檔時觸發。"
allowed-tools: Bash(python *), Bash(python3 *), Read
---

# Threads 認證設定

透過 Python 腳本產生 helper script，使用者在自己的 terminal 執行，Session ID 不經過對話。

## 工作流程

### Step 1：產生 setup script

執行以下指令：

```bash
python3 <skill-dir>/scripts/generate_setup.py
```

### Step 2：引導使用者

告訴使用者：

1. 開啟自己的 terminal
2. 執行 `bash <生成的 setup_threads.sh 的絕對路徑>`
3. 依照提示輸入 Session ID
4. 完成後**重啟 Claude Code** 才會生效

### Step 3：告知取得 Session ID 的方式

提供以下資訊：

- Session ID 有效期約 90 天
- 取得方式：
  1. 登入 https://www.threads.net
  2. F12 開啟 DevTools
  3. Application → Cookies → threads.net
  4. 複製 `sessionid` 的值
