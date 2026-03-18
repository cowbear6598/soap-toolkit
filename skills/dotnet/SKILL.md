---
name: backend
description: 當你在對後端 .NET 專案進行任何操作時使用
---

# 開發流程

1. 撰寫程式碼
2. 完成後執行 `dotnet test` 驗證
3. 若測試失敗，修正後再繼續
4. 確保所有測試通過才算完成

# 重要

- 有任何更動請補上測試，測試請依據測試規則撰寫
- **嚴禁使用 EF Core Migration**，你該提供的是 PostgreSql 語法
- 回傳是 PascalCase，前端接的時候要特別注意
- 使用通用 Response<T> 進行回傳

# 測試規則

- 命名以 Success_When_{Scenario}, Failed_When_{Scenario} 為規則
- 以**使用者情境**為主，而不是專注於邊界測試，也可以用 if 作為一個判斷依據來建立測試
- 只寫 IntegrationTest 不寫個別的測試
- 避免重複的測試，一個測試驗證完整的成功情境
- 相同邏輯路徑不需要分開測（如：有專案/無專案、有Cookie/無Cookie）
- 使用 Bogus 建立假資料

# 技術棧

- EF Core
- MediatR
- Shouldly
- FluentValdation
- ErrorOr
- NSubsitute
- Bogus

# Code Style

- 可讀性優先，再來是安全性，最後才是效能
- 純結構，如: Dto 優先使用 record 修飾詞
- 偏好 Early Return 以減少巢狀結構
- 偏好使用 enum 而非 magic strings
- 對於不會重新賦值的變數使用 `const`
- 優先使用 Include 和導航屬性而非手動 Join，沒有導航屬性需添加
- 偏好 inline 物件建立而非額外變數宣告
- 避免使用 Tuple 導致程式碼不好閱讀
- 資料轉換時須使用 Dto
- 不要過度使用 try-catch，你要使用的地方應該是無法預知的第三方服務，錯誤處理請用 early return 來達成

# Code Quality

- 徹底消除重複
- 透過命名和結構清楚表達意圖
- 保持方法精簡並專注於單一責任
- 最小化狀態和副作用
- 使用可能有效的最簡單解決方案
- 如果不需要上一個 async/await 的結果，使用並行的方式處理

# 效能與維護性

- 避免不必要的重複查詢與資源浪費
- 需考慮異步與快取機制

# class、struct、record 的選擇判斷

| 使用場景 | 建議類型   | 原因             |
|------|--------|----------------|
| 資料傳輸 | Record | 不可變性、值相等性、語法簡潔 |
| 值物件  | Record | 自動實作相等性比較      |
| 配置物件 | Record | 不可變性確保配置安全     |
| 業務實體 | Class  | 需要複雜行為和可變狀態    |
| 效能敏感 | Struct | 避免堆積配置         |

# 註解

僅對**複雜邏輯**加上註解：
- 計算複雜度分數：每個 `if`、`for` 或 `switch case` = 1 分
- 巢狀結構 = 分數加倍
- **只在分數超過 6 分時才加上註解**
- 註解應該解釋**為什麼**（原因），而不是**做什麼**（動作）
