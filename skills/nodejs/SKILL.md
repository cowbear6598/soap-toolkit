---
name: nodejs
description: 當你在對 node 專案進行任何操作時使用
---

# Nodejs + TypeScript 專案開發規範

## 流程規範

1. 先寫好測試的使用者情境有哪些即可
2. 開始實作功能
3. 開始完成測試
4. 執行 `bun run test` 直到功能都正常為止，**嚴禁**用投機取巧的方式通過測試，例如: skip
5. 執行 `bun run style` 檢查 code style 是正確的，有錯誤請修正，warning 也要修正

## 註解撰寫規則

- **嚴禁**亂填寫註解，只有複雜度高的才需要
- 複雜的程式碼才需要寫註解，判斷標準：
	- 一個 Method 有超過 **6 個以上**的判斷式（if/switch/三元運算符等）
	- 巢狀（nested）判斷式要**加倍計算**複雜度
- ✅ 寫**原因**（為什麼要這樣做），❌ 不要寫這段在做什麼

## Code Style

- 測試的 describe 使用 zh-TW 撰寫
- 優先使用 async / await
- 多達三個以上的地方使用相同方法、常數等，請抽共用
- 優先使用 early return
- 不要過度使用 try-catch，你要使用的地方應該是無法預知的第三方服務，錯誤處理請用 early return 來達成