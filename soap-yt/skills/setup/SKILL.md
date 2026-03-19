---
name: setup
description: 檢查 soap-yt 所需的工具是否已安裝，未安裝則提供安裝指引
---

# 工作流程

依序檢查以下工具，未安裝則顯示安裝指令：

| 工具 | 檢查方式 | 安裝指令 |
|------|---------|---------|
| yt-dlp | `which yt-dlp` | `brew install yt-dlp` |
| ffmpeg | `which ffmpeg` | `brew install ffmpeg` |
| faster-whisper | `python3 -c "import faster_whisper"` | `pip install faster-whisper` |
