#!/usr/bin/env python3
"""使用 faster-whisper 將影片語音轉為 SRT 字幕檔。"""

import argparse
import os
from faster_whisper import WhisperModel


def format_timestamp(seconds: float) -> str:
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02}:{int(m):02}:{s:06.3f}".replace(".", ",")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="影片檔案路徑")
    parser.add_argument("--language", default="zh", help="語言代碼 (zh/ja/en)")
    parser.add_argument("--model", default="medium", help="模型大小 (tiny/base/small/medium/large-v3)")
    args = parser.parse_args()

    model = WhisperModel(args.model, compute_type="int8")
    segments, _ = model.transcribe(args.video, language=args.language)

    srt_path = os.path.splitext(args.video)[0] + ".srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n")
            f.write(f"{seg.text.strip()}\n\n")

    print(f"字幕已輸出：{srt_path}")


if __name__ == "__main__":
    main()
