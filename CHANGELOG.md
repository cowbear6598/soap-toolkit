# Changelog

## [1.0.8] - 2026-03-21

### 新增
- download skill 新增自動字幕 fallback：沒有原生字幕時自動下載 YouTube 自動生成的英文字幕
- soap-chat 支援多 Bot，改用 config.json 管理 Bot 設定，取代 .env 單一 token 模式
- soap-chat plugin 在 marketplace.json 中註冊，支援透過 Slack Bot 發送訊息到頻道
- summary skill 改為 Slack mrkdwn 格式，以書的結構（目錄、章節）呈現全繁中摘要
- transcript skill 簡化為純 faster-whisper 本地辨識，預設模型改為 medium
- 調整 download 流程，影片與字幕分開下載，字幕優先順序 en → 中文 → 其他
- soap-dev 新增 output-styles/ 資料夾用於管理輸出風格設定，將 conductor.md 移至該目錄
- soap-yt plugin 支援 YouTube 影片下載、字幕取得、重點摘要、GIF 擷取、影片片段擷取
- 調整 soap-yt skills 目錄結構至 skills/ 資料夾下
- 重新命名 marketplace 為 soap-toolkit，新增 soap-jira plugin

## [1.0.4] - 2026-03-19

### 新增
- 新增 setup command，自動設定 plugin 所需權限

### 修正
- 移除有版權問題的音效檔案

## [1.0.2] - 2026-03-19

### 新增
- GitHub Actions release 工作流程
- release skill 版本號更新步驟

## [1.0.1] - 2026-03-19

### 修正
- 將 .DS_Store 加入 .gitignore 避免版本控制污染
- 完善 release skill 說明文件

## [1.0.0] - 2026-03-19

### 新增
- 初始化 soap-dev plugin
- 新增 marketplace 支援 plugin 安裝
- 新增 install-statusline 安裝指令
- 新增 install-hooks 安裝指令（format-on-save hook）
- 整合 review agents 為統一的 review skill（涵蓋複雜度、品質、安全性、風格、測試、冗餘六面向）
- 整合 plan agents 為統一的 plan skill（BDD User Flow + 前後端計畫書）
- 新增 code-implement skill（實作後自動偵測專案類型跑測試）
- 新增 git-push skill（統一 commit message 格式）
- 新增 release skill（自動產 CHANGELOG 並發版）
- 更新 statusline 價格計算，簡化為 opus/sonnet/haiku 最新版價格

### 修正
- 修正 marketplace source 格式與路徑問題
- 修正 plugin 遞迴 cache 導致 ENAMETOOLONG 錯誤，分離 marketplace 與 plugin 結構
