---
name: code-implement
description: "根據計畫書實作程式碼。當使用者說「開始實作」「按照計畫做」「implement」「開工」或想把計畫書轉為實際程式碼時觸發。"
allowed-tools: "Bash(dotnet *), Bash(npm *), Bash(bun *), Bash(go *), Bash(pytest *), Bash(python *), Bash(python3 *), Bash(cargo *), Task"
---

## Step 1：取得實作輸入來源

實作只從 plan 檔驅動。檢查專案內的 `tasks/frontend.md` 與 `tasks/backend.md`，若有任一有效則依其 Phase 結構執行；若皆不存在或皆無效，直接終止流程。

### 來源：Plan 檔

檢查專案內是否存在：

- `tasks/frontend.md`（前端計畫書）
- `tasks/backend.md`（後端計畫書）

讀取 plan 檔後**先驗證格式**：至少要能解析出一個 Phase 與其下的大項目。若檔案存在但空、格式錯誤、或無任何 Phase，視為**該 plan 檔無效**，繼續嘗試下一個 plan 檔；若兩份 plan 檔都不存在或皆無效，直接終止流程並回報使用者：「找不到有效的 plan 檔，請先跑 `/soap-dev:plan` 產出計畫，或跑 `/soap-dev:fix` 從 bug/review 結果自動修復」。明確告知使用者哪個 plan 檔被判定為無效及原因（例如「`tasks/frontend.md` 內容為空」或「`tasks/backend.md` 解析不到任何 Phase 標題」）。

只要任一個有效的 plan 檔存在，就採用「Plan 檔」來源，照既有的 Phase 結構走：

- `frontend.md` 和 `backend.md` 都有效就兩條線都處理；只有其中一個有效就只處理那一條。
- 同時讀取 `tasks/userflow.md` 作為背景知識傳給每個 Agent。若 `userflow.md` 不存在就略過，不視為錯誤。

## Step 2：按 Phase 依序執行

### 規則

計畫書的結構是用 Phase 分組，每個 Phase 內有大項目（A. B. C. ...），大項目下是具體的 Todo。

執行規則：

- **前端和後端是兩條獨立的執行線**：各自按自己的 Phase 順序推進，互不等待。前端 Phase 1 完成就直接進前端 Phase 2，不需要等後端。
  - 澄清：「互不等待」是指不同「Phase 進度」上互不阻塞；但若某個大項目在 prompt 中明確標註「需等待前端 / 後端 Phase N 完成」，則遵守該明確標註。
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

每個 Phase 結束後執行測試驗證。

1. **偵測專案類型並執行對應測試指令**：
   - 找到 `*.csproj` → 執行 `dotnet test`
   - 找到 `package.json`：
     - 先查看 `scripts.test`。若存在且不是預設的 `"exit 1"`，照 `npm test` / `bun test` 執行。
     - 若 `package.json` 存在但 `scripts.test` 不存在或是預設的 `exit 1`，視為「無測試設定」，按下方「完全找不到任何測試設定」規則處理。
   - 找到 `go.mod` → 執行 `go test ./...`
   - 以上都沒有 → 按下列清單搜尋測試設定檔：
     - `jest.config.*`
     - `vitest.config.*`
     - `pytest.ini`
     - `pyproject.toml` 的 `[tool.pytest.ini_options]`
     - `karma.conf.*`
     - `Makefile` 的 test target
     - `.github/workflows/*.yml` 中的 test step
   - 找到任一測試設定 → 照該工具執行對應測試指令。
   - **完全找不到任何測試設定**：直接跳過測試驗證，在回報中明確說「此專案未偵測到測試框架，跳過 Phase 驗證；使用者需自行手動測試」。不要無限迴圈、也不要自己產生測試檔。
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
