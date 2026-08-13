---
name: video-understand
description: 將本地影片或音訊轉錄成 SRT，並把字幕或 transcript 整理成摘要、重點、章節、翻譯或指定發布格式。當使用者要求理解、轉錄、摘要影片內容或建立時間章節時使用。
---

# Video Understand

按需執行轉錄或摘要；已有合適 transcript 時直接使用。

## Transcribe

```bash
python3 <skill-dir>/scripts/whisper_transcribe.py "/path/to/video.mp4" --language zh --model medium
```

依主要語言選擇 `zh`、`ja` 或 `en`；不確定且會影響品質時先確認。模型預設 `medium`，也支援 `tiny`、`base`、`small`、`large-v3`。保留時間戳。缺少 faster-whisper 時提供 `python3 -m pip install faster-whisper`，只有使用者明確要求才安裝。

## Summarize

先理解完整 transcript，再依用途產生摘要、重點、主題章節、翻譯、時間索引或指定發布格式。預設使用繁體中文與一般 Markdown；只有內容準備貼到 Slack 時才使用 Slack mrkdwn。未要求檔案時直接回覆，需要供後續工具使用時才寫入來源旁的文字檔。

- 依內容而非固定分鐘數劃分主題。
- 不加入 transcript 未支持的內容。
- 章節時間涵蓋相關字幕的第一句開始至最後一句結束。
- 使用 `MM:SS`，超過一小時使用 `H:MM:SS`。
