---
name: transcript
description: 使用 faster-whisper 對已下載的影片進行本地語音辨識，產生 SRT 字幕檔
---

# 工作流程

使用 faster-whisper 對影片進行本地語音辨識，輸出 SRT 字幕到影片所在資料夾。

需先確保影片已下載。

```bash
python3 <skill-dir>/scripts/whisper_transcribe.py "影片路徑.mp4" --language zh
```

- `--language`：語言代碼（zh/ja/en）
- `--model`：模型大小（預設 medium，可選 tiny/base/small/medium/large-v3）
