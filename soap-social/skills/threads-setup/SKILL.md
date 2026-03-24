---
name: threads-setup
description: "設定 Threads 的認證資訊。當使用者提到要設定 Threads session、設定 Threads token、setup threads、或提供 Threads session ID 要求存檔時觸發。"
allowed-tools: Read, Write, Edit
---

# Threads 認證設定

## 工作流程

### Step 1：接收 Session ID

從使用者訊息中取得 Threads 的 session ID。

### Step 2：寫入 .env

將 session ID 寫入 `<skill-dir>/../threads/.env`：

```
THREADS_SESSION_ID=使用者提供的值
```

如果 `.env` 已存在，只更新 `THREADS_SESSION_ID` 那一行，保留其他設定。
如果 `.env` 不存在，從 `<skill-dir>/../threads/.env.example` 複製一份再填入。

### Step 3：驗證

讀取 `.env` 確認已正確寫入，顯示設定完成的訊息。

## 注意事項

- Session ID 有效期約 90 天
- 過期時使用者需重新從 DevTools 取得：
  1. 登入 https://www.threads.net
  2. F12 → Application → Cookies → threads.net
  3. 複製 `sessionid` 的值
