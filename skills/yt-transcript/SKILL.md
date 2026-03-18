---
name: yt-transcript
description: 下載 YouTube 影片字幕時使用。優先抓 YouTube 字幕，沒有時用 whisper 本地辨識
---

# YouTube 字幕下載

優先從 YouTube 下載字幕，若無字幕則使用 whisper 本地辨識。

# 輸出位置

- 該歌曲所在的資料夾

## Step 1: 使用 yt-dlp 下載字幕

優先嘗試從 YouTube 下載字幕（包含自動字幕）。

### 語言優先順序

1. 繁體中文 (zh-Hant)
2. 日文 (ja)
3. 英文 (en)

### 完整指令範例

```bash
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hant,ja,en" --sub-format srt --skip-download -o "%(title)s.%(ext)s" "YouTube影片網址"
```

### 參數說明

- `--write-sub`: 下載字幕檔
- `--write-auto-sub`: 包含自動產生的字幕
- `--sub-lang "zh-Hant,ja,en"`: 字幕語言優先順序
- `--sub-format srt`: 使用 SRT 格式
- `--skip-download`: 只下載字幕，不下載影片

## Step 2: Fallback 使用 Whisper

如果 yt-dlp 無法取得字幕，則使用 whisper 進行本地語音辨識，優先使用中文，沒有則是英文

### 完整指令範例

```bash
whisper "影片路徑.mp4" --model small --language zh --output_format srt
```

### 參數說明

- `--model small`: 使用 small 模型（平衡速度與準確度）
- `--language ja`: 指定語言（ja=日文、zh=中文、en=英文）

### 輸出格式

Whisper 會輸出：
- `.srt`: 字幕檔（含時間軸）

## 完整工作流程範例

```bash
# 1. 先嘗試下載字幕
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hant,ja,en" --sub-format srt --skip-download -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 2. 如果沒有字幕，先下載影片（如果還沒下載）
yt-dlp -f "best[height<=720]" --no-playlist -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 3. 使用 whisper 辨識
whisper "影片標題.mp4" --model small --language ja --output_format srt
```
