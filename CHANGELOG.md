# Changelog

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
