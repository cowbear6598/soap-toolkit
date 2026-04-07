---
name: rss
description: "抓取 YouTube RSS feed 取得頻道最新影片列表。當使用者提到 rss、YouTube RSS、抓 RSS、取得最新影片、check rss、查看頻道更新、或想從 YouTube 頻道的 RSS feed 取得影片列表時觸發。即使使用者只說「看看有沒有新影片」或「頻道最近更新了什麼」，只要是在談論取得 YouTube 頻道的影片列表，就應該使用這個 skill。"
allowed-tools: WebFetch, Bash(sleep *)
---

# 工作流程

根據使用者提供的 Channel ID 清單，抓取 YouTube RSS feed、過濾 Shorts、依發布時間排序後輸出影片列表。

## Step 1: 解析使用者輸入

使用者會提供 Channel ID 與頻道名稱的對應，格式如：

```
UC6t1O76G0jYXOAoYCm153dA -> Lenny's Podcast
UC2ggjtuuWvxrHHHiaDH1dlQ -> Hung-yi Lee
```

從輸入中提取所有 Channel ID 與對應名稱。

## Step 2: 抓取 RSS Feed

對每個 Channel ID，使用 WebFetch 抓取：

```
https://www.youtube.com/feeds/videos.xml?channel_id=${channelId}
```

所有頻道**同時並行抓取**（在同一個回應中發出多個 WebFetch 呼叫）。

### 錯誤重試

如果任何頻道回傳 404 或 500：

1. 告知使用者哪些頻道失敗，正在等待重試
2. 使用 `sleep 600` 等待 10 分鐘
3. 重新抓取失敗的頻道
4. 重複直到所有頻道都成功

## Step 3: 解析 XML 並提取影片資料

從每個 RSS feed 的 XML 回應中，找出所有 `<entry>` 區塊，提取以下欄位：

| 欄位 | XML 路徑 | 說明 |
|------|----------|------|
| videoId | `<yt:videoId>` | YouTube 影片 ID |
| title | `<title>` | 影片標題 |
| url | `<link href="...">` | 影片網址 |
| publishedAt | `<published>` | 發布時間（ISO 8601） |
| description | `<media:group>` 內的 `<media:description>` | 影片描述（取前 100 字元） |
| channel | `<author>` 內的 `<name>` | 頻道名稱 |

## Step 4: 過濾 YouTube Shorts

排除符合以下任一條件的影片：

- 標題包含 `#shorts` 或 `#Shorts`
- 網址包含 `/shorts/`
- 描述包含 `#shorts`

## Step 5: 排序與輸出

1. 合併所有頻道的影片
2. 依 `publishedAt` 升冪排序（最舊的在最前面）
3. 以 Markdown 表格輸出：

```
| # | 頻道 | 標題 | 網址 | 發布時間 |
|---|------|------|------|----------|
| 1 | Lenny's Podcast | How to build... | https://youtube.com/watch?v=xxx | 2024-03-15 |
```

發布時間格式統一為 `YYYY-MM-DD`。
