---
name: review
description: "對程式碼進行全面 review，涵蓋複雜度、品質、安全性、風格、測試覆蓋、冗餘、效能、AI 可讀性八大面向。當使用者提到 review、code review、檢查程式碼、PR review、想確認程式碼品質，或只說「幫我看一下」「檢查一下有沒有問題」時都應觸發。但若使用者想在動手前討論方向（而非檢查已寫好的 code），請改用 discuss 或 plan。"
allowed-tools: Bash(git *), Bash(python3 *)
---

## 流程

### Step 1：了解變更範圍

**前置檢查**：若 git 工作樹沒有任何改動，主動詢問使用者要 review 哪些檔案、PR 網址、或具體程式碼片段再繼續。

執行以下兩個指令並合併去重取得本次改動的檔案清單：

1. `git diff --name-only HEAD` — tracked 的改動（staged + unstaged，包含 modified / added / deleted）
2. `git ls-files --others --exclude-standard` — untracked 的新增檔案（自動排除 .gitignore 規則）

兩份清單聯集去重後作為 changed files。若最終清單為空，返回「無需 review」訊息並終止整個流程，不得進入 Step 2。

註：deleted 檔案會在 Step 2 呼叫 closure.py 前的「過濾實體不存在路徑」步驟自然剔除，不需特別處理。

### Step 1.5：過濾計劃/spec 類 markdown

目的：把計劃書、規格、todo、release notes、會議記錄、CHANGELOG、進度回報、需求清單等「非程式碼類」的 markdown 從 changed files 中剔除，避免 Step 3 八個 review agent 浪費資源去檢查這類檔案。

執行步驟：

1. 從 Step 1 取得的 changed files 中篩出**所有副檔名為 `.md`** 的檔案。若沒有任何 .md 檔案 → 直接跳到 Step 2。
2. 對每個 .md 檔案**並行**啟動一個 Explore agent，`subagent_type: Explore`、`model: haiku`，prompt 見下方「haiku 過濾 Agent Prompt 模板」。
   - 並行上限：同一時刻最多啟動 8 個 haiku agent；.md 檔案數 > 8 時分批並行（每批 ≤ 8，前一批全部回收後再啟下一批）。原因：每個 agent 只做一次「讀 50 行 + 回 YES/NO」的 micro task，啟動開銷已逼近實際工作開銷，無上限的並行會讓 review skill 在 docs refactor 場景反而變慢、變貴。
3. 收齊所有 haiku agent 的回報後，依下列規則處理：
   - haiku 回 `YES` → 從 changed files 中**移除**該 .md
   - haiku 回 `NO` → 該 .md **保留**在 changed files 中
   - haiku 呼叫失敗（API error / timeout / 回傳格式不是 `YES` 或 `NO`）→ **fail close**：把該 .md 當作計劃類，從 changed files 中移除（理由：避免後續 8 個 review agent 為此白跑一輪；寧可漏 review 一份 .md，也不浪費 token）
4. 若有任何 .md 被剔除，向使用者回報：「跳過 X 個計劃類 md：[檔案清單]」（X 為剔除數量，清單列出所有被剔除的檔案路徑，含 fail close 的）
5. 過濾後的 changed files 若**完全為空**（所有改動都被剔除），返回「無需 review（所有改動皆為計劃類 md）」訊息並**終止整個流程**，不得進入 Step 2。

#### haiku 過濾 Agent Prompt 模板

```
請讀取檔案 {md_file_absolute_path} 的開頭前 50 行，判斷它是否屬於以下任一類型：

- 計劃文件（plan）
- 規格說明（spec）
- todo / 待辦清單
- release notes
- 會議記錄
- CHANGELOG
- 進度回報
- 需求清單

只回答一個英文單字：屬於以上任一類型回 `YES`，否則回 `NO`。不要任何其他文字、解釋或標點。
```

其中 `{md_file_absolute_path}` 替換為該 .md 檔案的絕對路徑。

### Step 2：計算依賴 closure

目的：對 Step 1 取得的 changed files 追蹤正向（它 import 了誰）與反向（誰 import 了它）import 依賴，把關聯檔案也納入 review 範圍，避免漏掉因改動而受影響的程式碼。

執行指令：

```
python3 {skill_dir}/scripts/closure.py {project_root} {changed_files...}
```

- `{skill_dir}` 替換為此 skill 的絕對路徑
- `{project_root}` 是當前 git repo 根目錄
- `{changed_files...}` 是 Step 1 從 `git diff` 拿到的清單（相對路徑），以空白分隔

**呼叫 closure.py 前先過濾掉實體檔案不存在的路徑**（例如 git diff 顯示但已被刪除的檔案、rename 後舊路徑），只把**實體存在**的檔案路徑傳入。

解析 stdout 的 JSON，取得三組資料：

- `changed`：本次使用者實際修改的檔案
- `related`：透過 import closure 追蹤出來的關聯檔案
- `unresolvable`：追蹤過程中無法解析的檔案清單（每筆含檔案路徑與原因）

#### 執行錯誤處理

- 若 closure.py **exit code 非 0**：讀取 stdout 嘗試解析為 JSON `{"error", "detail"}`。若能解析，將 `error` 與 `detail` 內容 verbose 回報給使用者並**終止流程**。若不能解析（例如 python3 未安裝、腳本檔案不存在、其他 shell 層級錯誤），直接把 stderr / stdout 原文 verbose 給使用者並**終止流程**。
- 若 exit code 為 0 但 stdout 不是合法 JSON，verbose 錯誤（含 stdout 原文）給使用者並**終止流程**。
- 若 JSON 解析成功但缺少 `changed`、`related`、`unresolvable` 任一欄位，verbose 錯誤給使用者並**終止流程**。

#### unresolvable verbose 回報規格

若 `unresolvable` 非空，**必須先以下列格式 verbose 回報給使用者**，然後繼續後續步驟（不得因此中止 review）：

呈現 `reason` 時的處理規則：

- reason 若包含換行字元，呈現前將換行替換成 `↩ `（或字面字串 `\n`）避免破版
- reason 若長度 > 200 字，截斷顯示前 200 字並加上 `...`
- reason 可能是 `; ` 串接多個錯誤訊息，原樣保留即可（套用上述長度/換行規則）

範例：

```
⚠️ 下列檔案無法納入依賴追蹤：
- src/x.py：SyntaxError line 3: ...
- src/y.custom：unsupported extension: .custom
- src/z.ts：cannot resolve import './a'; cannot resolve import './b'; parse error at line 42 ↩ unexpected token
- src/huge.py：<非常長的錯誤訊息前 200 字>...

Review 仍會以成功解析的檔案（改動 + 關聯）進行。
```

後續 review 範圍 = `changed` ∪ `related`；傳給 review agent 時**必須明確區分這兩組**，不可合併成一份清單。

#### 範圍為空的特殊處理

若 closure.py 輸出的 `changed` 清單為空（所有改動檔案都進了 unresolvable）且 `related` 也為空，review 範圍完全無檔案，此時向使用者回報並**終止流程**；若 `changed` 為空但 `related` 非空，則 review 照樣進行，只是沒有「改動檔案」section。

### Step 2.5：組裝需求描述

目的：為 Step 3 中第 8 個 AI 可讀性 Agent 準備「需求描述」資訊來源，讓該 agent 自行判斷命名是否與需求相符。此步驟只對第 8 個 agent 產生影響，其他七個 agent 不使用此資訊。

執行步驟：

1. 執行 `git log -1 --format=%B` 取得 HEAD commit message 原文（可能包含換行，取全文，不做截斷或過濾）
2. 從當前 session 上下文中擷取需求描述：往回掃描最近 5 輪對話，找以下任一 markdown 結構，找到第一個就停：
   - `# Plan` / `## User Flow` / `## 前端計畫` / `## 後端計畫`（plan 產出）
   - `# Bug 調查報告` / `## 根因` / `## 建議修復方向`（bug 產出）
   - `# Discuss 結論` / `## 結論`（discuss 產出）
   找到後取整段標題下內容（不超過 1500 字，超過就截斷）；找不到任何結構則該欄位傳空字串。
3. 將兩份資訊一併傳給第 8 個 AI 可讀性 agent（見 Step 3 的 prompt 模板）

重要：

- 主 agent **不對 commit message 進行「有料」判定**（不設字數門檻、不排除 fix/update 等字樣）
- 由 haiku agent 自己判斷兩份資訊何者更有用、或兩者皆無法提供足夠內容
- 若兩份資訊皆為空或無意義，由第 8 agent 判定後回報「資訊不足，跳過」

若 git log 指令失敗（例如尚無任何 commit），commit message 欄位傳空字串，流程照常進行。

### Step 3：平行啟動八個 Review Agent

使用 Agent tool 同時啟動以下八個 review。每個都使用 `subagent_type: Explore`，搭配指定的 model。

**範例**：以「複雜度」這個 review 為例，`{reference 檔案的完整路徑}` 會替換成此 skill references 目錄下的絕對路徑，例如：

```
請讀取 /Users/soap.fu/Desktop/soap-toolkit/soap-dev/skills/review/references/code-complex.md 了解你的檢查規則，然後對以下兩組檔案進行 review：
...（下略，依下方模板填入 changed / related 清單）
```

其他六個 review 同理，只是把 `code-complex.md` 換成對應的 reference 檔名。

給每個 agent 的 prompt 格式：

```
請讀取 {reference 檔案的完整路徑} 了解你的檢查規則，然後對以下兩組檔案進行 review：

[改動檔案]（本次 commit 實際修改的檔案，review 請以較嚴格標準）
{changed 清單}

[關聯檔案]（透過 import closure 被帶進範圍的檔案，review 只報「本次改動可能影響到」的問題；單純既有但與本次改動無關的問題不列出，避免把整個 codebase 的歷史問題一起抓回來）
{related 清單}

按照規則中指定的輸出格式回報結果，但每個問題需額外標註該檔案屬於「改動檔案」或「關聯檔案」。
```

八個 review：

> 註：第 8 個「AI 可讀性」Agent 的 prompt 模板與其他七個不同（多帶 commit message 原文與 session 摘要兩個欄位，詳見下方「第 8 個 Agent 的 Prompt 模板」）。

| Review | Reference | Model |
|--------|-----------|-------|
| 複雜度 | references/code-complex.md | sonnet |
| 品質 | references/code-quality.md | sonnet |
| 安全性 | references/code-security.md | sonnet |
| 風格 | references/code-style.md | haiku |
| 測試 | references/test-case.md | sonnet |
| 冗餘 | references/redundant.md | haiku |
| 效能 | references/performance.md | sonnet |
| AI 可讀性 | references/ai-readability.md | haiku |

reference 路徑以此 skill 的目錄為基準，給 agent 時請用完整絕對路徑。

#### 第 8 個 Agent（AI 可讀性）的 Prompt 模板

AI 可讀性 Agent 需要額外兩個欄位：commit message 原文與 session 摘要（來自 Step 2.5）。使用下列模板：

```
請讀取 {reference 檔案的完整路徑} 了解你的檢查規則和 grep 搜尋的具體方法。

請自行判斷哪份資訊更有用：
- 兩份都為空字串 → 回報「資訊不足，跳過」
- 至少一份能萃取出 ≥ 3 個與當前改動有關的具體名詞（功能名、API 名、領域詞彙），就用該份進行 AI 可讀性檢查
- 兩份都萃取不到 ≥ 3 個具體名詞（只剩「修一下」「update」「fix」這類無內容字眼）→ 回報「資訊不足，跳過」

[Commit Message 原文]
{commit_message_content}

[Session 上下文摘要]
{session_summary}

然後對以下兩組檔案進行 AI 可讀性檢查：

[改動檔案]
{changed 清單}

[關聯檔案]
{related 清單}

按照規則中指定的輸出格式回報結果。若你判定兩份資訊皆不足以萃取有意義的關鍵字，請直接回報「資訊不足，跳過」。
```

其中：
- `{reference 檔案的完整路徑}` 替換為 `references/ai-readability.md` 的絕對路徑
- `{commit_message_content}` 替換為 Step 2.5 取得的 commit message 原文（可能為空字串）
- `{session_summary}` 替換為 Step 2.5 摘要的 session 需求描述（可能為空字串）
- `{changed 清單}` 與 `{related 清單}` 同其他七個 Agent

重要：Agent 依下列規則自行判斷哪份資訊更有用：
- 兩份都為空字串 → 回報「資訊不足，跳過」
- 至少一份能萃取出 ≥ 3 個與當前改動有關的具體名詞（功能名、API 名、領域詞彙），就用該份進行 AI 可讀性檢查
- 兩份都萃取不到 ≥ 3 個具體名詞（只剩「修一下」「update」「fix」這類無內容字眼）→ 回報「資訊不足，跳過」

### Step 4：委派單一 Sonnet Agent 統包彙整與驗證

收齊 8 個 review agent 的結果後，主 agent **不做任何彙整動作、不打開任何原始碼檔案、不排除任何條目**，直接啟動 1 個 Sonnet Explore agent，把 8 份 agent 原始輸出原樣丟進 prompt，由該 Sonnet agent 一次做完兩件事：

1. **彙整**：把 8 份 agent 輸出合併為單一待驗證清單
2. **驗證**：逐條打開對應的原始碼檔案與行號，實際比對程式碼內容，判斷每一條「問題是否屬實 / 修正方向是否正確」

主 agent 在此階段不做任何抽驗或二次判斷：Sonnet 回報屬實 → 條目進修正表格；Sonnet 回報不屬實 → 條目進「✅ 排除誤判」區塊。Sonnet prompt 內已對「兩種結論、不設信心度、不准模糊用語」等規則做完整約束（見下方模板），主 agent 信任其結果即可。

啟動參數：

- `subagent_type: Explore`
- `model: sonnet`
- prompt 見下方「Sonnet 統包 Agent Prompt 模板」

#### Sonnet 統包 Agent Prompt 模板

```
你是 review 統包 agent，任務分為「彙整」與「驗證」兩階段，一次完成。

====== 階段一：彙整 ======

以下提供 8 個 review agent 的完整原始輸出（依序：複雜度、品質、安全性、風格、測試、冗餘、效能、AI 可讀性）。請合併為單一待驗證清單，規則：

1. 逐條保留欄位：面向、檔案、行號、問題描述、建議修正方向、「所屬」標記（「改動檔案」或「關聯檔案」，原樣沿用 review agent 的標記）
2. AI 可讀性 Agent 的結果與其他 7 個面向並列處理，不單獨成段；其「建議調整命名」視同其他面向的修正項目（面向欄填「AI 可讀性」）
3. AI 可讀性的「狀態欄」三擇一判定（直接套用，不需讀其他檔案）：
   - 該 agent 回「資訊不足，跳過」 → 狀態 = `ℹ️ 資訊不足`，不產出任何修正條目
   - 該 agent 回報有命名建議 → 狀態 = `⚠️ 建議調整`，命名建議轉為修正條目（面向欄填「AI 可讀性」）
   - 該 agent 回報命名與需求一致、無需調整 → 狀態 = `✅ OK`，不產出修正條目
   若有疑義（例如 agent 同時提了「沒問題但建議調整」的混合表述），讀 references/ai-readability.md 的「與統包 agent 的介面契約」節仲裁。

====== 階段二：驗證 ======

對彙整後的每一條待驗證條目，逐條打開對應的原始碼檔案與行號，實際比對程式碼內容，判斷：

1. review agent 描述的問題是否屬實
2. review agent 建議的修正方向是否正確

判斷規則：

- 每一條只有「屬實」或「不屬實」兩種結論，不設信心度、不設「不確定」、不設「需再確認」
- 排除（不屬實）的合法理由只有兩個：問題本身不存在、修正方向錯誤
- 若檔案不存在、行號越界、或檔案為二進位無法解析，判為「不屬實」，排除理由必須以「檔案/行號已失效：<具體原因>」開頭，例如「檔案/行號已失效：src/x.py 已被刪除」「檔案/行號已失效：行號 240 越界（該檔僅 180 行）」。原因：這類條目代表 review agent 拿到的檔案快照與當前 codebase 不一致，已不可能驗證，但下游主 agent 仍需把它列入「排除誤判」區塊讓使用者知道發生過，不可直接吞掉。
- **嚴禁**以「非本次改動引入」「既有問題」「歷史遺留」為由判為不屬實。原因：review 範圍已由 closure.py 擴到 related 檔案，有意納入這些「既有」但受改動影響的程式碼；若容許以此為由排除，會讓 related 擴展形同虛設。
- **嚴禁**使用「看起來可能是」「應該是」「或許」「有可能」這類模糊用語。每個結論的理由必須直接引用實際讀到的程式碼內容作為依據。原因：下游主 agent 已被設計為「完全信任 Sonnet 回報」，不做二次抽驗。若你留下模糊結論，主 agent 會把不確定判斷直接帶入最終修正表格，污染整份 review 結果。
- 「所屬」欄位（改動檔案 / 關聯檔案）必須原樣保留原 review agent 的標記，不得自行變動或推斷。原因：最終輸出要依「所屬」欄分流到「改動檔案」「關聯檔案」兩個 section，一旦變動會讓分流錯誤，使用者看不到真正影響範圍。
- 針對 AI 可讀性面向（建議調整命名）的條目，驗證標準一致：原命名確實模糊/與需求脫節 → 屬實；原命名其實合理（例如 `utils.py` 裡放的本來就是通用工具） → 不屬實

====== 回報格式（直接輸出，不要加其他說明文字）======

## AI 可讀性狀態
（三擇一：✅ OK / ⚠️ 建議調整 / ℹ️ 資訊不足）

## 屬實清單
| # | 面向 | 檔案 | 行數 | 問題 | 建議 | 所屬 |
|---|------|------|------|------|------|------|
（逐條列出屬實條目，「所屬」欄原樣沿用 review agent 標記）

## 不屬實清單
| # | 面向 | 檔案 | 行數 | 原本問題 | 排除理由 |
|---|------|------|------|----------|----------|
（逐條列出不屬實條目，排除理由必須引用具體程式碼事實）

---

[8 個 review agent 的完整原始輸出]
{all_8_agent_outputs}
```

其中 `{all_8_agent_outputs}` 替換為 Step 3 收到的 8 份 agent 回報原文，依序：複雜度、品質、安全性、風格、測試、冗餘、效能、AI 可讀性。主 agent **不得**對這 8 份輸出做任何預處理或篩選。

主 agent 收到 Sonnet 回報後，直接進入輸出格式組裝：
- 屬實清單 → 依「所屬」欄分流填入「改動檔案」「關聯檔案」的 🔴 修正表格
- 不屬實清單 → 填入「✅ 排除誤判」區塊
- 「AI 可讀性狀態」欄位 → 填入「📊 統計」相關欄位與「🔍 AI 可讀性」section

### 輸出格式

```markdown
# Code Review 結果

## 改動檔案

### 🔴 修正
| # | 面向 | 檔案 | 行數 | 問題 | 建議 |
|---|------|------|------|------|------|

## 關聯檔案

### 🔴 修正
| # | 面向 | 檔案 | 行數 | 問題 | 建議 |
|---|------|------|------|------|------|

## ✅ 排除誤判
- [檔案:行號] 原本問題：... / 排除理由：...

## 📊 統計
- 改動檔案數：X1
- 關聯檔案數：X2
- 修正：Y
- 排除誤判：W
- 無法解析檔案：U（若 > 0 需列出檔案與原因）
- AI 可讀性狀態：✅ OK / ⚠️ 建議調整 / ℹ️ 跳過

## 🔍 AI 可讀性
- 命中率：X%（命中 / 總關鍵字）
- 關鍵字命中明細：[可用表格或列表]
- 狀態：✅ OK / ⚠️ 建議調整 / ℹ️ 資訊不足（擇一）
```

註：「改動檔案」與「關聯檔案」兩個 section 的修正表格中，`面向`欄位允許包含「AI 可讀性」。
