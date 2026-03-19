---
name: gif
description: 使用 ffmpeg 從影片的指定時間範圍擷取 GIF 動圖
---

# 工作流程

1. 讀取 `summary.md` 中各段落的時間範圍，從影片擷取 GIF 到 `./gifs/`
2. 產生 `index.html` 卡片頁面，3 欄 Grid 排列，每張卡片包含段落標題與 GIF

輸出位置：影片所在資料夾。每個 GIF 建議不超過 10 秒。

## 擷取指令

```bash
mkdir -p ./gifs
ffmpeg -ss HH:MM:SS -t 秒數 -i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/001.gif
```

## HTML 卡片結構

```html
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px;">
  <div class="card">
    <h3>段落標題</h3>
    <img src="./gifs/001.gif" />
  </div>
  <!-- 重複每個段落 -->
</div>
```
