---
name: rss
description: "抓取 YouTube RSS feed 取得頻道最新影片列表。當使用者提到 rss、YouTube RSS、抓 RSS、取得最新影片、check rss、查看頻道更新、或想從 YouTube 頻道的 RSS feed 取得影片列表時觸發。即使使用者只說「看看有沒有新影片」或「頻道最近更新了什麼」，只要是在談論取得 YouTube 頻道的影片列表，就應該使用這個 skill。"
allowed-tools: Bash(python3 *)
---

# YouTube RSS Feed 查詢

透過 Python 腳本抓取 YouTube 頻道的 RSS feed。腳本位於 `<skill-dir>/scripts/`，執行前將 `<skill-dir>` 替換為實際絕對路徑。

## 腳本一覽

| 腳本 | 用途 | 必填參數 |
|------|------|----------|
| `fetch_rss.py` | 抓取 YouTube RSS feed | `--channels`（一或多個 Channel ID） |

## 使用範例

```bash
# 抓取多個頻道
python3 <skill-dir>/scripts/fetch_rss.py --channels UC6t1O76G0jYXOAoYCm153dA UC2ggjtuuWvxrHHHiaDH1dlQ UCbo-KbSjJDG6JWQ_MTZ_rNA
```

## 輸出格式

所有輸出皆為 JSON。錯誤時輸出 `{"error": "...", "detail": {...}}`。

### fetch_rss.py 回傳欄位

`total`（影片數量）, `videos`（每筆含 `videoId`, `title`, `url`, `publishedAt`, `description`, `channel`）

影片已過濾 YouTube Shorts，並依 `publishedAt` 升冪排序（最舊優先）。

## 輸出呈現

收到 JSON 結果後，以 Markdown 表格呈現：

| # | 頻道 | 標題 | 網址 | videoId | 發布時間 |
|---|------|------|------|---------|----------|

發布時間格式統一為 `YYYY-MM-DD`。

## 注意事項

- 不要在執行腳本前檢查環境變數。直接執行腳本，腳本內部已有完整的錯誤處理。
- 如果 RSS feed 回傳 404 或 500，腳本會自動等待 1 分鐘後重試，直到成功為止，無需手動處理。
