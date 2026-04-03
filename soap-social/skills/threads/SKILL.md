---
name: threads
description: "爬取 Threads 用戶貼文。當使用者提到 Threads、爬文、抓貼文、或想取得 Threads 上某人的貼文時觸發。即使使用者只說「幫我看一下某人的 Threads」或「抓一下他的貼文」，只要涉及 Threads 平台的內容取得，就應該使用這個 skill。"
allowed-tools: Bash(python3 *)
---

# Threads Skill

透過 Python 腳本爬取 Threads 用戶貼文。所有腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 腳本一覽

| 腳本 | 用途 | 必填參數 | 選填參數 |
|------|------|----------|----------|
| `fetch.py` | 抓取用戶最新貼文 | `--user` | `--count`（預設 20，上限約 15 篇） |

## 工作流程

### Step 1：解析用戶名

從使用者提供的資訊中解析出 Threads 用戶名，支援以下格式：
- `https://www.threads.com/@username` → `username`
- `@username` → `username`
- `username` → `username`

### Step 2：執行爬取

```bash
python3 <skill-dir>/scripts/fetch.py --user username --count 20
```

### Step 3：格式化顯示

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

- 用戶不存在：顯示找不到該用戶
- 網路錯誤：顯示請求失敗原因

## 注意事項

- **免 cookie 方式**：腳本使用 Googlebot UA 抓取 SSR HTML，不需要任何認證或環境變數。
- **貼文數量上限**：SSR 頁面最多回傳約 15 篇貼文，無法分頁，指定超過此數的 `--count` 也不會有更多結果。
