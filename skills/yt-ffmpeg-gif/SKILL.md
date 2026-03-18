---
name: yt-ffmpeg-gif
description: 使用 ffmpeg 從影片的指定時間範圍擷取 GIF 動圖
---

# 工作流程

1. 從影片中擷取指定時間範圍的 GIF 動圖
2. 產生簡易的 html，包含段落與 Gif 以卡片顯示，每個 Grid 的行數是三張

# 輸出位置

- 該歌曲所在的資料夾裡面

## 基本指令格式

```bash
ffmpeg -ss 開始時間 -t 秒數 -i 影片路徑 -vf "fps=10,scale=480:-1" output.gif
```

## 參數說明

- `-ss`: 開始時間（格式：HH:MM:SS 或 MM:SS）
- `-t`: 持續秒數（整數）
- `-i`: 輸入影片路徑
- `-vf "fps=10,scale=480:-1"`: 視訊濾鏡
  - `fps=10`: 10 幀每秒（降低檔案大小）
  - `scale=480:-1`: 寬度 480px，高度等比例縮放

## 完整指令範例

### 範例 1: 從 00:00 開始，擷取 30 秒

```bash
ffmpeg -ss 00:00:00 -t 30 -i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/001.gif
```

### 範例 2: 從 02:30 開始，擷取 2 分鐘（120 秒）

```bash
ffmpeg -ss 00:02:30 -t 120 -i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/002.gif
```

### 範例 3: 從 15:45 開始，擷取 45 秒

```bash
ffmpeg -ss 00:15:45 -t 45 -i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/003.gif
```

## 輸出資料夾

建議將所有 GIF 統一存放在 `./gifs/` 資料夾：

```bash
# 先建立資料夾（如果不存在）
mkdir -p ./gifs

# 然後產生 GIF
ffmpeg -ss 00:00:00 -t 30 -i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/001.gif
```

## 與 yt-summary 配合使用

根據 `yt-summary` 產生的報告時間戳，批次產生 GIF：

```markdown
## 段落一：開場介紹（00:00 - 02:30）
→ ffmpeg -ss 00:00:00 -t 10 -i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/001.gif

## 段落二：主題說明（02:30 - 05:10）
→ ffmpeg -ss 00:02:30 -t 10-i "影片.mp4" -vf "fps=10,scale=480:-1" ./gifs/002.gif
```

## 注意事項

- 時間格式必須是 `HH:MM:SS`（如 00:02:30）
- 持續時間 `-t` 使用秒數（如 10 = 10秒）
- 檔案大小取決於影片長度和內容複雜度
- 建議每個 GIF 不超過 10 秒鐘，以控制檔案大小
