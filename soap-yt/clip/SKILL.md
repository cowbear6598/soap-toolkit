---
name: clip
description: 使用 ffmpeg 從影片擷取指定時間範圍的片段（mp4）
---

# 工作流程

從影片中擷取指定時間範圍的片段，輸出到影片所在資料夾的 `./clips/`。

## 指令

```bash
mkdir -p ./clips
ffmpeg -ss HH:MM:SS -t 秒數 -i "影片.mp4" -c copy ./clips/001.mp4
```

`-c copy` 不重新編碼，速度快但起止點可能有幾秒偏差。若需精確切割，改用：

```bash
ffmpeg -ss HH:MM:SS -t 秒數 -i "影片.mp4" -c:v libx264 -c:a aac ./clips/001.mp4
```
