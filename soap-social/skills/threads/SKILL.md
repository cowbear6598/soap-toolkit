---
name: threads
description: "爬取 Threads 用戶貼文。當使用者提到 Threads、爬文、抓貼文、或想取得 Threads 上某人的貼文時觸發。即使使用者只說「幫我看一下某人的 Threads」或「抓一下他的貼文」，只要涉及 Threads 平台的內容取得，就應該使用這個 skill。"
allowed-tools: Bash(python *), Bash(python3 *)
---

# Threads Skill

透過 Python 腳本爬取 Threads 用戶貼文。所有腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 腳本一覽

| 腳本 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `fetch.py` | 抓取用戶最新貼文 | `--user` | `--count`（預設 20） |

## 工作流程

### Step 1：檢查環境設定

確認 `<skill-dir>/.env` 存在且包含 `THREADS_SESSION_ID`。若沒有：
1. 複製 `<skill-dir>/.env.example` 為 `<skill-dir>/.env`
2. 引導使用者從 DevTools 取得 sessionid：
   - 登入 https://www.threads.net
   - F12 → Application → Cookies → threads.net → 複製 `sessionid` 的值
3. 填入 `.env` 後再繼續

### Step 2：解析用戶名

從使用者提供的資訊中解析出 Threads 用戶名，支援以下格式：
- `https://www.threads.net/@username` → `username`
- `@username` → `username`
- `username` → `username`

### Step 3：執行爬取

```bash
python <skill-dir>/scripts/fetch.py --user username --count 20
```

### Step 4：格式化顯示

將 JSON 結果格式化顯示在 CLI，每篇貼文顯示：
- 發文時間
- 文字內容（過長則截斷）
- 媒體數量（圖片/影片）
- 互動數（按讚、回覆）

## 輸出格式

所有腳本輸出皆為 JSON。錯誤時輸出 `{"error": "..."}`。

### fetch.py 回傳欄位

`user`（用戶名）, `count`（實際數量）, `posts`（每筆含 `id`, `text`, `timestamp`, `media`, `likes`, `replies`）

## 錯誤處理

- Token 過期（401/403）：提示使用者重新從 DevTools 取得 sessionid
- 用戶不存在：顯示找不到該用戶
- 網路錯誤：顯示請求失敗原因
