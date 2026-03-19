---
name: transcript
description: 下載 YouTube 影片字幕時使用。優先抓 YouTube 字幕，沒有時用 faster-whisper 本地辨識
---

# 工作流程

輸出 SRT 字幕到影片所在資料夾。語言優先順序：繁體中文 > 日文 > 英文。

**務必先執行 Step 1**，只有在 yt-dlp 確認無字幕時才進入 Step 2。

## Step 1: yt-dlp 下載 YouTube 字幕（優先）

```bash
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hant,ja,en" --sub-format srt --skip-download -o "%(title)s.%(ext)s" "YouTube影片網址"
```

確認是否產生 `.srt` 檔。有的話就結束，不需要 Step 2。

## Step 2: Fallback — faster-whisper 本地辨識

僅在 Step 1 無法取得字幕時使用。需先確保影片已下載。

使用本 skill 附帶的腳本：

```bash
python3 <skill-dir>/scripts/whisper_transcribe.py "影片路徑.mp4" --language zh
```

會在影片同目錄輸出 `.srt` 檔。可用 `--model` 指定模型大小（預設 small）。
