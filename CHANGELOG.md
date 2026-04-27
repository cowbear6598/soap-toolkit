# Changelog

## [1.3.0] - 2026-04-28

### 新增
- plan skill 新增「Fallback / Defensive Code 防護規則」，計畫書產出時若 todo 出現 try-catch、null fallback、預設值兜底、retry 或 TS 型別已保證的防衛，必須先用 AskUserQuestion 與使用者對齊每一個的必要性，對齊通過才能寫入 todo（第三方服務、I/O、網路請求等真實邊界例外可直接寫入）
- review skill code-quality 面向新增「Fallback 必要性」檢查項，列出程式碼中所有 fallback / defensive code 並標註「必要 / 可移除 / 需確認」，於 review 結果中獨立成一個區塊輸出

## [1.0.17] - 2026-04-13

### 新增
- closure.py 擴充 10 個語言支援：Vue（SFC）、Svelte、Astro、Java、Kotlin、Swift、Dart、Ruby、PHP、C/C++
- SFC 類 (Vue/Svelte/Astro) 能抽取 `<script>` 區塊與 Astro `---` frontmatter 後套 TS/JS 解析
- 新增 Dart pubspec.yaml、PHP composer.json (PSR-4)、Ruby Gemfile、Java pom.xml / build.gradle、C/C++ include 等 manifest 解析器

### 修正
- closure.py：UnicodeDecodeError 改為靜默略過，不再進 unresolvable（解決 HLS 視訊切片 .ts 檔與 TypeScript 撞名的偽陽性雜訊）

## [1.0.16] - 2026-04-13

### 修正
- closure.py：重新定義 unresolvable 語意，外部 import（stdlib / 未列入 manifest 的第三方）改為靜默略過，不再進 unresolvable，解決無 manifest 專案的 Python/Node/Go stdlib import 產生大量雜訊
- closure.py：relative import 解析失敗（含被註解掉的 import）改為靜默略過，不再產生偽陽性 unresolvable；unresolvable 現在僅保留真正壞掉的情況（讀檔失敗、不支援副檔名、腳本內例外）

## [1.0.15] - 2026-04-13

### 新增
- soap-dev:review 新增 Step 2，透過 `scripts/closure.py` 追蹤 import 依賴 closure，支援正向+反向關聯、無限深度、循環偵測、語言感知排除第三方
- 新增 `scripts/closure.py` 純 Python stdlib 依賴追蹤器，支援 TS/JS/Python/C#/Go/Rust，無法解析不靜默 fallback
- soap-dev:code-implement Step 1 改為三來源判定（Plan 檔 → Conversation context → 反問），支援「三問判準」、plan/context 優先級規則、測試框架偵測擴充
- review 和 code-implement skills 增加 frontmatter 權限：review 加 `git *` + `python3 *`；code-implement 加 Bash test 指令 + Task

## [1.0.10] - 2026-03-21

### 修正
- install-hooks 還原為只安裝 format-on-save
- code-implement skill 移除 PreToolUse hooks（清理檢查指令）

## [1.0.9] - 2026-03-21

### 新增
- code-implement skill 新增 PreToolUse hooks 驗證 Bash、Edit、Write 等工具的執行安全性
- git-push skill 增強自動檢查功能：支援專案類型自動偵測，執行相應的測試與檢查指令

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
