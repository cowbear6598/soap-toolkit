---
name: review
description: "對程式碼進行全面 review，涵蓋複雜度、品質、安全性、風格、測試覆蓋、冗餘程式碼六大面向。當使用者提到 review、code review、檢查程式碼、PR review、或想確認程式碼品質時觸發。即使使用者只說「幫我看一下」或「檢查一下有沒有問題」，只要是在談論程式碼品質，就應該使用這個 skill。"
---

## 流程

### Step 1：了解變更範圍

執行 `git diff --name-only HEAD` 取得本次改動的檔案清單（包含 staged 和 unstaged）。如果沒有任何變更，直接告訴使用者沒有需要 review 的內容。

### Step 2：平行啟動六個 Review

使用 Agent tool 同時啟動以下六個 review。每個都使用 `subagent_type: Explore`，搭配指定的 model。

給每個 agent 的 prompt 格式：

```
請讀取 {reference 檔案的完整路徑} 了解你的檢查規則，然後對以下檔案進行 review：

{改動的檔案清單}

按照規則中指定的輸出格式回報結果。
```

六個 review：

| Review | Reference | Model |
|--------|-----------|-------|
| 複雜度 | references/code-complex.md | sonnet |
| 品質 | references/code-quality.md | sonnet |
| 安全性 | references/code-security.md | sonnet |
| 風格 | references/code-style.md | haiku |
| 測試 | references/test-case.md | sonnet |
| 冗餘 | references/redundant.md | haiku |

reference 路徑以此 skill 的目錄為基準，給 agent 時請用完整絕對路徑。

### Step 3：彙整與判斷

收到所有 agent 的結果後，逐一檢視每個問題：

1. **判斷是否為誤判** — 有些問題可能是 agent 過度敏感，結合上下文判斷是否真的需要修
2. **每個問題只有「要修」和「不用修」** — 不給「可修可不修」「需確認」「視情況而定」這種模稜兩可的選項。如果你無法確定，就自己去讀程式碼搞清楚，然後做出明確判斷。不確定不是一個選項。

### 輸出格式

```markdown
# Code Review 結果

## 需要修正的問題

### 🔴 必須修正
| # | 面向 | 檔案 | 行數 | 問題 | 建議 |
|---|------|------|------|------|------|
| 1 | 安全性 | UserController.cs | 45 | SQL Injection | 使用參數化查詢 |

### 🟡 建議修正
| # | 面向 | 檔案 | 行數 | 問題 | 建議 |
|---|------|------|------|------|------|
| 2 | 風格 | OrderService.cs | 12 | magic string | 改用 enum |

## ✅ 無問題（已排除誤判）
- 複雜度：無問題
- 測試：覆蓋完整
- ...

## 📊 統計
- 檢查檔案數：X
- 必須修正：Y
- 建議修正：Z
- 排除誤判：W
```
