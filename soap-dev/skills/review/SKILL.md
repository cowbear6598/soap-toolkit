---
name: review
description: "對程式碼進行全面 review，涵蓋複雜度、品質、安全性、風格、測試覆蓋、冗餘程式碼、效能七大面向。當使用者提到 review、code review、檢查程式碼、PR review、或想確認程式碼品質時觸發。即使使用者只說「幫我看一下」或「檢查一下有沒有問題」，只要是在談論程式碼品質，就應該使用這個 skill。"
allowed-tools: Bash(git *), Bash(python3 *)
---

## 流程

### Step 1：了解變更範圍

執行以下兩個指令並合併去重取得本次改動的檔案清單：

1. `git diff --name-only HEAD` — tracked 的改動（staged + unstaged，包含 modified / added / deleted）
2. `git ls-files --others --exclude-standard` — untracked 的新增檔案（自動排除 .gitignore 規則）

兩份清單聯集去重後作為 changed files。若最終清單為空，返回「無需 review」訊息並終止整個流程，不得進入 Step 2。

註：deleted 檔案會在 Step 2 呼叫 closure.py 前的「過濾實體不存在路徑」步驟自然剔除，不需特別處理。

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

### Step 3：平行啟動七個 Review

使用 Agent tool 同時啟動以下七個 review。每個都使用 `subagent_type: Explore`，搭配指定的 model。

**範例**：以「複雜度」這個 review 為例，`{reference 檔案的完整路徑}` 會替換成此 skill references 目錄下的絕對路徑，例如：

```
請讀取 /Users/soap.fu/Desktop/soap-toolkit/soap-dev/skills/review/references/code-complex.md 了解你的檢查規則，然後對以下兩組檔案進行 review：
...（下略，依下方模板填入 changed / related 清單）
```

其他六個 review 同理，只是把 `code-complex.md` 換成對應的 reference 檔名。

給每個 agent 的 prompt 格式：

```
請讀取 {reference 檔案的完整路徑} 了解你的檢查規則，然後對以下兩組檔案進行 review：

[改動檔案]
{changed 清單}

[關聯檔案]
{related 清單}

按照規則中指定的輸出格式回報結果，但每個問題需額外標註該檔案屬於「改動檔案」或「關聯檔案」。
```

七個 review：

| Review | Reference | Model |
|--------|-----------|-------|
| 複雜度 | references/code-complex.md | sonnet |
| 品質 | references/code-quality.md | sonnet |
| 安全性 | references/code-security.md | sonnet |
| 風格 | references/code-style.md | haiku |
| 測試 | references/test-case.md | sonnet |
| 冗餘 | references/redundant.md | haiku |
| 效能 | references/performance.md | sonnet |

reference 路徑以此 skill 的目錄為基準，給 agent 時請用完整絕對路徑。

### Step 4：彙整與判斷

收到所有 agent 的結果後，逐一檢視每個問題，並同時讀取 agent 回報中每個問題所屬的「改動檔案 / 關聯檔案」標記：

1. **判斷是否為誤判** — 有些問題可能是 agent 過度敏感，結合上下文判斷是否真的需要修
2. **每個問題只有「要修」和「不用修」** — 不給「可修可不修」「需確認」「視情況而定」這種模稜兩可的選項。如果你無法確定，就自己去讀程式碼搞清楚，然後做出明確判斷。不確定不是一個選項。

### Step 5：逐條驗證

主 agent 對 Step 4 初步彙整後的每一條修正項目，逐條打開對應的原始碼檔案與行號，實際比對程式碼內容，確認以下兩點：

1. review agent 描述的問題是否屬實
2. review agent 建議的修正方向是否正確

驗證時用語必須嚴謹，**不允許「看起來可能是」「應該是」「或許」這類模糊判斷**，主 agent 必須給出明確結論：問題屬實或不屬實、修正方向正確或不正確。

若驗證後發現 review agent 判斷錯誤（問題不存在、或建議的修正方向錯誤），**直接從修正清單排除該項目**，並在最終輸出的「✅ 排除誤判」區塊記錄：檔案、行號、原本問題描述、排除理由。

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
```
