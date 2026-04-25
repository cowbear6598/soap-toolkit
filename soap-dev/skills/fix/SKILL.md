---
name: fix
description: "把對話中最近一次的 bug 分析或 review 結果自動轉成程式碼修復。當使用者說「fix」「修」「修好」「修正」「修復」「自動修」「照那份報告改」「把剛剛 review 的問題處理掉」，或在 bug 調查 / code review 之後直接要求動手改程式碼時觸發。但若對話中沒有 bug 或 review 報告（只有 plan 或新功能討論），請改用 code-implement 而不是 fix。"
allowed-tools: "Task, Bash(git *), Bash(dotnet *), Bash(npm *), Bash(bun *), Bash(go *), Bash(pytest *), Bash(python *), Bash(python3 *), Bash(cargo *)"
---

fix 與 code-implement 的差別：fix 吃 bug/review 報告，code-implement 吃 plan。fix 不自動推送修復後的變更（只在 review 來源時，於修復前推一次基準版）。

## Step 1：偵測來源

掃描對話 context 最近一輪輸出，找出 bug 分析或 review 結果。

### bug 來源線索

最近一輪出現以下 bug 報告 markdown 結構任一組合：

- `# Bug 調查報告`
- `## 問題描述`
- `## 使用者操作路徑`
- `## 呼叫鏈追蹤`
- `## 根因`
- `## 影響範圍`
- `## 建議修復方向`

### review 來源線索

最近一輪出現以下 review 結果 markdown 結構任一組合：

- `# Code Review 結果`
- `## 改動檔案`
- `## 關聯檔案`
- `### 🔴 修正`
- `## 📊 統計`
- `## 🔍 AI 可讀性`

### 判定規則

- **兩者都沒有** → 終止流程，回報使用者：「找不到 bug 分析或 review 結果，請先跑 `/soap-dev:bug` 或 `/soap-dev:review` 再回來呼叫 `/soap-dev:fix`」
- **兩者都有** → 以**對話中最後出現的那一份**為主（依該份在訊息中的位置，不是依 markdown 順序）；若同一輪訊息內兩者並存，反問使用者「這次想 fix bug 報告還是 review 結果？」並等待回覆，不得自行擇一

## Step 2：依來源分支

### 來源 = bug

直接跳到 Step 3，**完全不執行 git-push**。

### 來源 = review

先執行 git-push 流程保留當前基準版：

- 使用 Task tool 啟動通用 agent（不指定 subagent_type），`model: haiku`
- prompt 要求 agent 完整讀取並遵守 `soap-dev/skills/git-push/SKILL.md` 的流程：刪除無用 md、偵測專案類型跑所有檢查指令、任一失敗就停、全通過才 `git add .` → commit → push
- commit message 使用 `[Fix]` 或 `[Refactor]` 標籤，描述為「保留 review 前基準版」
- agent 回報失敗（lint/test 任一未通過，或任何 push 失敗原因） → fix 流程停止，verbose 失敗原因給使用者，明確告知「請先修好未通過的檢查再重新呼叫 `/soap-dev:fix`」，**不得進入 Step 3**
- agent 回報 push 成功 → 繼續 Step 3

## Step 3：從報告抽出修復項目清單

從 Step 1 偵測到的 bug 或 review 報告中逐項抽取修復項目，結果**僅留在記憶體**，不寫入任何檔案，也不產生 `tasks/frontend.md` / `tasks/backend.md`。

### 每個項目至少含三欄

- **檔案路徑**（若報告含行號要一併帶上，格式 `file_path:line_number`）
- **要做的改動**（行為與規格描述，不貼程式碼）
- **驗收條件或對應問題來源**（例如「review 必須修正項 #3」或「bug 報告中根因指向的空字串處理」）

### 報告不夠具體時

若報告**沒有具體檔案路徑或改動描述**（例如 bug 只寫「這裡有問題」卻沒點出哪個檔案；review 只有「整體品質不佳」卻沒指出具體檔案與問題） → fix 終止流程，回報使用者：「bug/review 報告不夠具體，缺少可修復的明確項目，請補充細節後重新呼叫 `/soap-dev:fix`」

### 不覆寫既有檔案

本步驟不會覆寫任何既有的 `tasks/*.md` 檔案。

## Step 4：分批啟動 agent 依序修復

### 切批規則

把 Step 3 抽出的修復項目清單，**按原始順序每 10 項切成一批**：

- 第 1～10 項 → 批 1
- 第 11～20 項 → 批 2
- 以此類推，最後一批不足 10 項照樣成批
- **修復項目總數 ≤ 10** → 只切出單一批，行為等同原本「整包丟一個 agent」的版本（不需做任何特殊判斷，自然走完批 1 即結束）

### 順序執行

- **嚴格順序、絕不並行**：批 1 完成 → 啟動批 2；批 2 完成 → 啟動批 3；以此類推。前一批 agent 未回報結束之前，**絕不**啟動下一批。
- **每批用全新 agent**：每批都使用 Task tool（**不指定 subagent_type**，`model: sonnet` 固定寫死）啟動一個全新 agent。Task tool 本來就會在新 agent 開乾淨 context，不需要做任何 reset 動作；要做的事是 **不要在 prompt 裡塞前批的進度摘要、修改清單或產出回顧**。前批的成果只透過實際被修改的檔案在 codebase 中體現，下一批 agent 透過 grep / read 自行從檔案讀到最新狀態。
- **同一批內依序處理**：同一個 agent 從該批第一項做到該批最後一項，做完一項再做下一項，絕不把同一批切開分給多個 agent。

### 傳給每批 agent 的 prompt 必須包含以下三個部分

1. **本批修復項目的完整清單**：把該批（最多 10 項）的每個修復項目都列進來，每項含檔案路徑（含行號若有）、要做的改動（行為與規格描述）、驗收條件或問題來源。要具體到檔案與要做的改動，不得只丟模糊描述，並明確要求 agent 依清單順序逐項完成。
2. **userflow 相關情境**：若 `tasks/userflow.md` 存在，從中擷取與本批修復項目相關的段落傳入；若 `tasks/userflow.md` 不存在，此部分省略、不視為錯誤。
3. **實作規則**：完整貼入以下四條
   - 實作前必須用 grep / read 重新定位要改的程式碼位置，**絕不直接信任清單裡寫的行號**。原因：fix 是分批順序執行（見 Step 4 切批規則），前一批 agent 可能已改動過同一檔案造成行號位移；同時 review/bug 報告產出到 fix 啟動之間使用者也可能手動編輯。grep/read 是唯一可靠的當下定位方式。
   - 計畫書提供方向，但實作時會遇到未提到的細節，要自己查閱 codebase 確認再動手；發現修復項目描述有不合理處，以實際 codebase 為準
   - 實作中不要產出任何 summary / plan / task 等 markdown 檔案
   - 專注寫程式碼，不是寫文件

### 全部批次完成後

所有批次依序跑完且皆回報成功 → 進 Step 5 執行測試（**測試只在所有批次跑完後執行一次，不要每批都跑測試**）。

## Step 5：測試驗證

所有修復完成後，執行測試驗證。

### 偵測專案類型並執行對應測試指令

從 repo 根目錄起，**找到任何符合的設定檔就要跑對應指令**（多語言 monorepo 可能同時觸發多條，全部都要跑、不可只挑一個）：

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
- 找到任一測試設定 → 照該工具執行對應測試指令
- **完全找不到任何測試設定** → 直接跳過測試驗證，回報「此專案未偵測到測試框架，跳過驗證；使用者需自行手動測試」。不要無限迴圈、也不要自己產生測試檔。

### 測試結果處理

- **測試失敗** → 依原規則循環修正：為失敗點啟動新的修復 agent、修完重跑測試。**循環修正同樣套用 Step 4 的分批規則**：失敗點 ≤ 10 項走單批；> 10 項則一樣每 10 項一批、順序執行、新 agent 不傳承；且同樣適用「不要信清單行號、永遠 grep/read 找實際位置」規則。

  **循環上限**：連續 3 輪「修完→測試還是失敗」就停止，verbose 列出「每一輪修了什麼、為何沒改善」給使用者並反問是否要繼續、改變策略、或放棄。原因：若 3 輪都修不掉同一組失敗，通常是修復方向錯了或失敗點根因超出 bug/review 報告涵蓋範圍，繼續硬修只會擴大破壞面、燒 token，主動煞車交回使用者判斷比較理性。
- **測試通過** → 進 Step 6

## Step 6：收尾回報

**不自動執行 git-push**。

### 回報格式

- 已完成的修復項目清單（檔案、改動摘要）
- 測試驗證結果（通過 / 跳過 / 失敗後循環的最終結果）
- 明確提示「修復完成，請在本機驗測後自行呼叫 `/soap-dev:git-push` 推送」
- 若 Step 1 判定來源為 review，額外補一句「基準版本已在 Step 2 推上遠端，可供對照」

## 使用者後續操作提示

- 修復完成後使用者可自行呼叫 `/soap-dev:git-push` 推送。
- 若發現修改不如預期 → 重跑 `/soap-dev:bug` 或 `/soap-dev:review` 再呼叫 `/soap-dev:fix`；若前次為 review 來源，Step 2 推上遠端的基準版仍在遠端可供對照。
