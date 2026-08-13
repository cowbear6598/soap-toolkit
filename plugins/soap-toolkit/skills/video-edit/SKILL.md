---
name: video-edit
description: 使用 ffmpeg 從本地影片擷取一個或多個 mp4 片段或 GIF，並可依要求建立 GIF gallery。當使用者要求剪片、依時間戳擷取片段、製作 GIF 或動圖預覽時使用。
---

# Video Edit

直接使用使用者指定或已確認的時間範圍，不要求先下載、轉錄或摘要。

## Clip

快速切割可使用 stream copy；精確起止點或 copy 結果不佳時重新編碼：

```bash
ffmpeg -ss HH:MM:SS -t SECONDS -i "/path/to/video.mp4" -c copy "/path/to/output.mp4"
ffmpeg -ss HH:MM:SS -t SECONDS -i "/path/to/video.mp4" -c:v libx264 -c:a aac "/path/to/output.mp4"
```

Stream copy 可能因 keyframe 產生數秒偏差。

## GIF

```bash
ffmpeg -ss HH:MM:SS -t SECONDS -i "/path/to/video.mp4" -vf "fps=10,scale=480:-1" "/path/to/output.gif"
```

10 秒、10 fps、480px 寬只是預設；依分享平台調整時長、尺寸、fps 與品質。只有需要多段或 gallery 時才批次產生 GIF 或 HTML。

遵循使用者指定的輸出位置；否則使用來源旁的 `clips/` 或 `gifs/`。不要覆蓋既有檔案。缺少 `ffmpeg` 時提供 `brew install ffmpeg`，只有使用者明確要求才安裝。
