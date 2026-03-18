---
name: vue
description: 當你在對前端 Vue 專案進行任何操作時使用
---

# 主要流程

1. 先寫好測試的使用者情境有哪些即可
2. 開始實作功能
3. 開始完成測試
4. 執行 `bun run test` 直到功能都正常為止，**嚴禁**用投機取巧的方式通過測試，例如: skip
5. 執行 `bun run style` 檢查 code style 是正確的，有錯誤請修正，warning 也要修正

# i18n 規範

- 新增 UI 文字時，同步更新：
  - `src/i18n/locales/zh-TW.ts`
  - `src/i18n/locales/en.ts`
  - etc...
- 使用 `t('key')` 取得翻譯
- 確保所有新增的翻譯 key 在兩個語言檔案中都存在

# 註解撰寫規則

- **嚴禁**亂填寫註解，只有複雜度高的才需要
- 複雜的程式碼才需要寫註解，判斷標準：
	- 一個 Method 有超過 **6 個以上**的判斷式（if/switch/三元運算符等）
	- 巢狀（nested）判斷式要**加倍計算**複雜度
- ✅ 寫**原因**（為什麼要這樣做），❌ 不要寫這段在做什麼

# CSS 規範

## 命名規則
- 明確定義 class 名稱，例如：`win98-title`、`modal-header`
- 使用有意義且一致的命名慣例
- 與後端的 Request, Response 都是 PascalCase 為主

## 檔案組織
- 樣式統一放在 `styles/` 資料夾
- 依據功能分類放在不同 CSS 檔案

## Code Style

- composables 有共用方法，優先從裡面找尋相關功能
- import 使用 `@` 別名而不是絕對路徑
- 不要把 <div> 包在不允許的 Element 裡面，例如: <button> 等
- 優先使用 async / await
- 優先使用 early return
- 多達三個以上的地方使用相同方法、常數等，請抽共用
- 不要過度使用 try-catch，你要使用的地方應該是無法預知的第三方服務，錯誤處理請用 early return 來達成
- 盡量明確定義型別，**嚴禁**輕鬆帶過或使用泛型別

## Vue Component 職責分離

- Vue Component **只負責顯示邏輯**
- 核心商業邏輯或操作請抽出到 `.ts` 檔案

## 其他規範

- 你不需要執行 `bun run dev`，這會由使用者自行架設
