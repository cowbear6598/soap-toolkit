# Changelog

## [1.0.18] - 2026-04-14

### 新增
- **soap-dev:review skill 重構分類與驗證流程** — 取消「建議修正」分類，合併為單一「修正」；Step 3 prompt 拿掉關聯檔案降級說明；新增 Step 5 逐條驗證原始碼、排除誤判；輸出格式簡化
- **closure.py 新增 CSS 家族支援** — 支援 .css / .scss / .sass / .less 依賴追蹤，解析 @import（含 url() 與 media query）、SCSS @use / @forward、partial 慣例；TS/JS 能跨語言追到 CSS，外部 scheme（~、http(s)://、data:、//）靜默跳過

## [1.0.17] - 2025-12-XX

### 新增
- closure.py 擴充 10 個語言支援：Vue（SFC）、Svelte、Astro、Java、Kotlin、Swift、Dart、Ruby、PHP、C/C++
- SFC 類能抽取 `<script>` 區塊與 Astro `---` frontmatter 後套 TS/JS 解析
- 新增多個 manifest 解析器（pubspec.yaml/composer.json/Gemfile/pom.xml/build.gradle/include）
- closure.py：UnicodeDecodeError 改為靜默略過，解決 HLS 視訊切片 .ts 與 TypeScript 撞名的偽陽性雜訊

## [1.0.16] - 2025-11-XX

### 修復
- closure.py 重新定義 unresolvable 語意，外部 import（stdlib / 未列入 manifest 的第三方）改為靜默略過
- closure.py relative import 解析失敗改靜默，不再產生偽陽性；unresolvable 現在僅保留真正壞掉的情況
