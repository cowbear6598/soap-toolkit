---
name: yt-download
description: 使用 yt-dlp 下載 YouTube 影片時使用
---

# 工作流程

1. 使用 yt-dlp 下載 YouTube 影片。
2. 根據影片名稱取一個好聽一點的資料夾名稱並把影片丟進去，使用英文

# 輸出位置範例

- 影片名稱: 搞笑影片，那他的路徑就會在 `工作目錄/FunnyVideo/xxxxx.mp4`

# 基本設定

- 預設下載 720p 畫質
- 自動避免下載整個播放清單
- 輸出檔名使用影片標題

## 完整指令範例

```bash
yt-dlp -f "best[height<=720]" --no-playlist -o "%(title)s.%(ext)s" "YouTube影片網址"
```

## 參數說明

- `-f "best[height<=720]"`: 選擇最佳品質但不超過 720p 的影片
- `--no-playlist`: 只下載單一影片，即使該影片在播放清單中
- `-o "%(title)s.%(ext)s"`: 輸出檔名格式為「影片標題.副檔名」

## 使用範例

```bash
yt-dlp -f "best[height<=720]" --no-playlist -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```
