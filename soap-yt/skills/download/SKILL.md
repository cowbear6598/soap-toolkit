---
name: download
description: 使用 yt-dlp 下載 YouTube 影片及字幕時使用
---

# 工作流程

1. 根據影片名稱建立英文資料夾（如 `FunnyVideo/`）
2. 下載影片（720p）
3. 查看可用字幕，下載原生字幕

影片與字幕分開下載，避免字幕失敗導致影片下載中斷。

## Step 1: 建立資料夾 & 下載影片

```bash
mkdir -p "資料夾名稱"
yt-dlp -f "best[height<=720]" --no-playlist -o "資料夾名稱/%(title)s.%(ext)s" "YouTube影片網址"
```

## Step 2: 查看可用字幕

```bash
yt-dlp --list-subs --no-playlist "YouTube影片網址"
```

輸出會分成兩區：
- **Available subtitles**：原生字幕（作者上傳的）
- **Available automatic captions**：YouTube AI 自動生成的

## Step 3: 下載字幕

### 3a: 優先下載原生字幕

依優先順序：**en → 中文（zh, zh-Hant, zh-Hans）→ 其他原生字幕**

從 Step 2 的 **Available subtitles** 區找出有哪些原生字幕，按上述優先順序組合語言碼：

```bash
yt-dlp --write-sub --sub-lang "語言碼" --sub-format srt --skip-download -o "資料夾名稱/%(title)s.%(ext)s" "YouTube影片網址"
```

### 3b: 沒有原生字幕時，fallback 抓自動生成字幕

如果 Step 2 的 **Available subtitles** 區為空（沒有原生字幕），改為下載自動生成的英文字幕。

優先順序：**en-orig → en**

```bash
yt-dlp --write-auto-sub --sub-lang "en-orig,en" --sub-format srt --skip-download -o "資料夾名稱/%(title)s.%(ext)s" "YouTube影片網址"
```

下載後告知使用者：「此字幕為 YouTube 自動生成，非原生字幕。」

## 錯誤處理

字幕下載失敗（如 429 限流），最多重試 3 次。3 次都失敗就跳過字幕，不再嘗試。
