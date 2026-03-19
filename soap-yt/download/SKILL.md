---
name: download
description: 使用 yt-dlp 下載 YouTube 影片時使用
---

# 工作流程

1. 根據影片名稱建立英文資料夾（如 `FunnyVideo/`）
2. 下載影片（720p）到該資料夾

## 指令

```bash
mkdir -p "資料夾名稱"
yt-dlp -f "best[height<=720]" --no-playlist -o "資料夾名稱/%(title)s.%(ext)s" "YouTube影片網址"
```
