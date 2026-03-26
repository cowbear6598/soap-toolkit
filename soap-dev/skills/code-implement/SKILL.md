---
name: code-implement
description: "根據計畫書實作程式碼。當使用者說「開始實作」「按照計畫做」「implement」「開工」或想把計畫書轉為實際程式碼時觸發。"
---

## Step 1：讀取計畫書

讀取以下檔案：

- `tasks/frontend.md`（前端計畫書，可能不存在）
- `tasks/backend.md`（後端計畫書，可能不存在）
- `tasks/userflow.md`（使用者情境，作為實作的背景知識）

如果 `frontend.md` 和 `backend.md` 都存在就兩條線都處理；只有其中一個就只處理那一條。`userflow.md` 不直接實作，但要把相關情境傳給每個 Agent 讓它理解業務背景。

## Step 2：按 Phase 依序執行

計畫書的結構是用 Phase 分組，每個 Phase 內有大項目（A. B. C. ...），大項目下是具體的 Todo。

執行規則：

- **前端和後端是兩條獨立的執行線**：各自按自己的 Phase 順序推進，互不等待。前端 Phase 1 完成就直接進前端 Phase 2，不需要等後端。
- **同一條線內，Phase 必須依序完成**：Phase 1 的所有大項目全部完成後，才能推進到 Phase 2。
- **同一個 Phase 內的並行規則**：
  - 如果 Phase 標題標註了「可並行」，該 Phase 內的大項目可以同時啟動多個 Agent。
  - 如果 Phase 標題沒有標註「可並行」，該 Phase 內的大項目必須依序執行（A 完成後才啟動 B，B 完成後才啟動 C）。

## Step 3：啟動 Agent

每個大項目（A. B. C. ...）啟動一個獨立的 Agent。使用通用 agent（不指定 subagent_type），model 設為 sonnet。

### 嚴格遵守的原則

- **一個 Agent 只負責一個大項目**。絕對不要把多個大項目塞進同一個 Agent。
- **不要假設 Agent 知道任何背景**。Agent 是全新的，沒有讀過計畫書、沒有看過 codebase，所有需要的資訊都必須寫進 prompt。

### 傳給 Agent 的 prompt 必須包含以下三個部分

1. **該大項目的完整 Todo 內容**：把計畫書中該大項目底下的所有 Todo 原封不動貼進去，讓 Agent 知道要做什麼。
2. **userflow.md 的相關情境**：從 userflow.md 中擷取與該大項目相關的使用者情境，讓 Agent 理解為什麼要做這些事、使用者會怎麼操作。
3. **實作規則**：把下方「實作規則」區塊的內容完整貼進 prompt。

## Step 4：Phase 完成後驗證

每個 Phase 的所有 Agent 都完成後（不論是並行還是依序），執行測試驗證：

1. **偵測專案類型並執行對應測試指令**：
   - 找到 `*.csproj` → 執行 `dotnet test`
   - 找到 `package.json` → 查看 scripts 裡的 test 指令（`npm test` / `bun test` 等）
   - 找到 `go.mod` → 執行 `go test ./...`
   - 以上都沒有 → 搜尋 codebase 中的測試設定檔來判斷如何跑測試
2. **測試通過才進入下一個 Phase**。
3. **測試失敗就修正，修完再跑測試，重複直到全部通過**。只有測試全部通過後，才能推進到下一個 Phase。

---

## 實作規則

以下規則必須完整傳給每一個 Agent：

### 實作前

- 善用搜尋工具了解程式碼的依賴關係和既有架構。
- 計畫書提供方向，但實作時會遇到計畫書沒提到的細節，要自己查閱 codebase 確認再動手。
- 如果發現計畫書有不合理的地方，以實際 codebase 為準，不要盲目照抄計畫書。

### 實作中

- 不要產出任何 summary、plan、task 等 markdown 檔案。
- 專注在寫程式碼，不是寫文件。
