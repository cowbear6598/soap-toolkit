---
name: youtube
description: 查詢 YouTube 頻道近期影片，或使用 yt-dlp 下載單一影片、音訊、原生字幕與自動字幕。當使用者要求查看頻道更新、比較近期內容、取得 YouTube metadata，或下載 YouTube 媒體與字幕時使用。
---

# YouTube

只執行使用者需要的查詢或下載；已有適用的本地檔案時直接使用。

## Channel videos

```bash
python3 <skill-dir>/scripts/fetch_rss.py --channels CHANNEL_ID [CHANNEL_ID ...]
```

每個 Channel ID 最多取得近期 15 部影片，排除短於 60 秒或標題含 `#shorts` 的內容。依問題篩選結果，不強制固定版型或自動下載。只有 URL 或 handle 時先解析 Channel ID。腳本會每 60 秒重試失敗頻道；持續失敗時停止並回報，避免無限等待。

## Download

```bash
# 影片，預設最高 720p
yt-dlp -f "best[height<=720]" --no-playlist -o "/output/%(title)s.%(ext)s" "YOUTUBE_URL"

# 查詢或下載原生字幕
yt-dlp --list-subs --no-playlist "YOUTUBE_URL"
yt-dlp --write-sub --sub-lang "LANGUAGE_CODE" --sub-format srt --skip-download -o "/output/%(title)s.%(ext)s" "YOUTUBE_URL"

# 沒有合適原生字幕時使用自動字幕
yt-dlp --write-auto-sub --sub-lang "en-orig,en" --sub-format srt --skip-download -o "/output/%(title)s.%(ext)s" "YOUTUBE_URL"
```

遵循指定的格式、品質、語言和輸出位置。未指定字幕語言時，選擇適合後續任務的原生字幕；自動字幕必須標示。影片與字幕分開執行，暫時性字幕錯誤最多重試三次。預設不下載 playlist 或覆蓋檔案。

缺少 `yt-dlp` 時提供 `brew install yt-dlp`，只有使用者明確要求才安裝。
