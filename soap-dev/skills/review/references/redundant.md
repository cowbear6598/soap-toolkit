# 冗餘程式碼 Review 規則

## 檢查範圍

僅檢查本次有異動的程式碼。

## 檢查項目

本面向**只檢查 Haiku 在 changed + related 檔案範圍內可以高信心驗證的項目**。以下四類為檢查目標：

### 1. 未使用的 import

檔案頂部 import / using 宣告，但檔案內容沒有使用到。

### 2. 註解掉的程式碼

被 `//`、`#`、`/* */` 包起來且明顯是 code（不是說明文字）的區塊。應刪除，版控會記錄歷史。

### 3. Function 內的未使用 local variable

**僅限同一個 function / method scope 內**宣告且未使用的 local variable。

不檢查：
- module-level 變數
- class field
- export 出去的東西

（這些可能被外部使用，Haiku 看不到完整呼叫鏈，誤判機率高。）

### 4. 多餘的註解

- 註解描述「做什麼」而非「為什麼」
- 程式碼本身夠清晰就不需要註解
- 只有邏輯複雜到需要解釋背景 / 決策原因才值得寫

---

## 不檢查的項目

本面向**不檢查**以下項目（Haiku 在 changed + related 檔案範圍內無法可靠驗證，容易假陽性）：

- 未被呼叫的 method / function（可能被框架隱式呼叫、decorator 觸發、外部 repo 使用）
- Module-level 的 unused export / 變數（可能是 public API）

## 輸出格式

```markdown
## 冗餘程式碼 Review 結果

### ❌ 未使用的程式碼
| 檔案 | 行數 | 類型 | 內容 |
|------|------|------|------|
| path/to/file.cs | 3 | import | 未使用的 using System.Linq |
| path/to/file.ts | 45 | local variable | function foo 內宣告但未使用的 tempResult |
| path/to/file.py | 88 | commented code | 被註解掉的舊版邏輯區塊 |

### ⚠️ 多餘的註解
| 檔案 | 行數 | 註解內容 | 原因 |
|------|------|----------|------|
| path/to/file.cs | 12 | // 取得使用者 | 描述 what 而非 why |

```

「未使用的程式碼」表格的「類型」欄位僅限：`import`、`local variable`、`commented code` 三種，不應出現 `function` / `method` / `export` 等本面向不檢查的類型。

若沒有任何問題，回報單行「無問題」即可，不列檔案清單或表格。
