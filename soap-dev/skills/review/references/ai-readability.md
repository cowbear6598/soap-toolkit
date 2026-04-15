# AI 可讀性 Review 規則

## 1. 概述

### 目的

檢查程式碼中的命名（檔名、函式名、變數名、類別名、註解）與需求描述的一致性，藉此評估 AI（以及未來協作者）對本次改動的可讀性。當命名能直接反映需求中的核心概念，AI 才能在後續維護、debug、擴充功能時快速定位到正確的程式碼。

### 執行流程總覽

```
接收需求 → 判斷資訊充分性 → 萃取關鍵字 → 使用 Grep tool 搜尋 → 統計命中率 → 輸出建議
```

### 重要強調

**必須真實執行 Grep tool 搜尋，不能憑想像判斷。** 任何「我覺得這個關鍵字應該有命中」的揣測都不算數，每一個關鍵字都要實際透過 Grep tool 在 changed / related 檔案範圍內驗證。

---

## 2. 資訊充分性判定

Agent 會收到兩份資訊：

1. **commit message 原文**
2. **session 上下文摘要**

### 判定流程

- 兩份資訊都非空且能萃取出有意義概念 → 採用更完整、更具體的那份
- 只有一份有料 → 採用有料的那份
- 兩份都空，或皆無意義（例如只含 `fix`、`update`、`wip`、`test`、`tmp` 等短字、無實際語意）→ 直接輸出「ℹ️ 資訊不足，跳過 AI 可讀性檢查」並結束本檢查

### 補充

不設硬性字數門檻，由 agent 綜合判斷需求是否足以萃取出可被搜尋的概念。重點不是字數多寡，而是「能不能形成可被 grep 的關鍵字」。

---

## 3. 關鍵字萃取規則

### 萃取原則

從有效的需求描述中萃取核心關鍵字（名詞、動詞、概念詞），排除虛詞（冠詞、介系詞、連詞、助詞）。

### 中英混合處理

中英混合的需求描述：

- 英文概念直接取用（例如 `token`、`OAuth`、`webhook`）
- 中文概念要考慮其在程式碼中常見的英譯：
  - 「認證」→ `authentication` / `auth`
  - 「使用者」→ `user`
  - 「權限」→ `permission`
  - 「驗證」→ `verify` / `validate`
  - 「登入」→ `login` / `signin`

### 數量目標

萃取 **3 ~ 8 個關鍵字** 為宜。

### 失敗處理

- **完全萃取不出（0 個關鍵字）** → 輸出「ℹ️ 資訊不足，跳過 AI 可讀性檢查」並結束
- **萃取出 1 ~ 2 個** → 照常用這幾個進行 grep 搜尋與命中率計算（無字數下限規則）
- **萃取出 3+ 個** → 標準流程

---

## 4. Grep 搜尋策略

### 工具強制規定

**強制使用 Claude Code 內建的 Grep tool，不得使用 Bash 的 `grep` / `rg` 指令。** Grep tool 已針對權限與索引最佳化，使用 Bash 替代會讓結果不一致也無法正確涵蓋大型 codebase。

### 搜尋範圍

僅限 **changed 清單 + related 清單** 的檔案，不可擴及整個 repo。

### 搜尋對象

- 檔名
- 函式名
- 變數名
- 類別名
- 註解

### 對每個關鍵字的搜尋步驟

1. 先用 **Glob** 檢查是否有檔名包含該關鍵字（檔名層級命中）
2. 再用 **Grep tool** 檢查檔案內容是否有該關鍵字（內容層級命中）

### 大小寫與命名風格考量

- 做 **case-insensitive** 搜尋
- 同時嘗試命名風格變體：
  - `snake_case`：例如 `user_auth`
  - `camelCase`：例如 `userAuth`
  - `PascalCase`：例如 `UserAuth`

### 命中判定

搜尋結果以「該關鍵字是否至少在一個檔案中命中」為判定（檔名或內容皆可，任一風格變體皆可）。

---

## 5. 命中率計算

### 公式

```
命中率 = (命中關鍵字數 / 總萃取關鍵字數) × 100%
```

### 判定門檻

| 命中率 | 判定 |
|--------|------|
| `≥ 60%` | ✅ AI 可讀性 OK |
| `< 60%` | ⚠️ 建議調整命名 |

### 命中定義

一個關鍵字只要在 changed 或 related 的任一檔案（檔名或內容）中以任何命名風格變體被 grep 到，即計為命中一次。同一關鍵字不重複計數，無論在多少檔案中出現。

---

## 6. 命名調整建議

當命中率 `< 60%` 時，**必須**列出：

### 1. 所有未命中關鍵字清單

清楚列出哪些核心概念在程式碼中找不到對應命名。

### 2. 對應改名建議（具體到檔案路徑）

範例：

- 檔案：`utils.py` → `auth_utils.py`
- 函式：`do_stuff()` → `check_user_permission()`
- 變數：`u` → `user`
- 類別：`Manager` → `TokenManager`

### 建議風格

新命名應 **直接反映需求中的核心概念**，避免模糊的通用詞：

- ❌ `utils`、`helper`、`data`、`process`、`thing`、`stuff`、`manager`（無前綴）、`handler`（無前綴）
- ✅ `auth_utils`、`token_helper`、`user_data`、`process_payment`、`UserPermission`、`TokenManager`

---

## 7. 輸出格式與範例

### 範例 A：命中率 ≥ 60%（標準輸出）

```markdown
## AI 可讀性

**命中率**：75% (3/4)

| 關鍵字 | 命中狀態 | 命中檔案 |
|--------|---------|---------|
| authentication | ✅ 命中 | src/user_authentication.py, src/auth_utils.py |
| token | ✅ 命中 | src/auth_token_manager.py |
| verify | ❌ 未命中 | - |
| user | ✅ 命中 | src/user_authentication.py |

**結論**：✅ AI 可讀性 OK - 關鍵字命中率 75%

**命名調整建議**：
- `verify`: 考慮在 auth 流程中加入明確的 verify 函式（例如 `verify_token()`）
```

### 範例 B：命中率 < 60%（含完整調整建議）

```markdown
## AI 可讀性

**命中率**：20% (1/5)

| 關鍵字 | 命中狀態 | 命中檔案 |
|--------|---------|---------|
| permission | ✅ 命中 | src/permission.py |
| user | ❌ 未命中 | - |
| role | ❌ 未命中 | - |
| check | ❌ 未命中 | - |
| access | ❌ 未命中 | - |

**結論**：⚠️ 建議調整命名 - 命中率僅 20%，遠低於 60% 門檻

**命名調整建議**：

| 未命中關鍵字 | 建議調整位置 | 調整前 → 調整後 |
|--------------|--------------|------------------|
| user | src/utils.py | `utils.py` → `user_utils.py` |
| user | src/utils.py:12 函式 | `do_stuff(u)` → `get_user_info(user)` |
| role | src/manager.py 類別 | `Manager` → `RoleManager` |
| check | src/manager.py:30 函式 | `process()` → `check_role_access()` |
| access | src/helper.py 變數 | `data` → `access_record` |

**整體建議**：避免使用 `utils`、`helper`、`manager`、`do_stuff`、`process` 等模糊命名，改以需求中的核心概念（user / role / permission / access）為主詞構造命名。
```

### 範例 C：資訊不足

```markdown
ℹ️ 資訊不足，跳過 AI 可讀性檢查
```

---

## 8. 特殊情況處理

### Changed 與 Related 皆為空

不會執行到本 agent（由 Step 2 提前終止），故此情況本檢查不處理。

### Grep 對所有關鍵字都未找到任何匹配

回報：

```markdown
## AI 可讀性

**命中率**：0%

⚠️ 無法在程式碼中找到與需求相關的關鍵字 - 命中率 0%
```

並接著給出 **全面的命名調整建議**（針對所有萃取出的關鍵字逐一給出檔案/函式/變數的具體改名建議）。

### 關鍵字完全萃取不出

等同「資訊不足」，回報：

```markdown
ℹ️ 資訊不足，跳過 AI 可讀性檢查
```

---

## 9. 範例情景

### 情景 1：需求充分、命名良好、關鍵字 1 ~ 2 個

- 需求：「修正 token 解析時的 timezone 錯誤」
- 萃取：`token`、`timezone`
- Grep 結果：兩個都命中
- 輸出：✅ 命中率 100% (2/2)

### 情景 2：需求充分、命名良好、關鍵字 5 個

- 需求：「新增使用者權限驗證流程，支援 OAuth token 與 session」
- 萃取：`user`、`permission`、`verify`、`token`、`session`
- Grep 結果：4 個命中、1 個未命中
- 輸出：✅ 命中率 80% (4/5)，附上未命中關鍵字的小建議

### 情景 3：需求充分、命名模糊（全是 utils/helper）

- 需求：「實作後台訂單退款流程，包含金流回呼與通知」
- 萃取：`order`、`refund`、`payment`、`callback`、`notification`
- Grep 結果：1 / 5 命中（只有 `payment` 命中，其他檔案都叫 `utils.py`、`helper.py`、`manager.py`、`do_stuff()`）
- 輸出：⚠️ 命中率 20% + 完整命名調整建議表

### 情景 4：commit 與 session 兩份皆空

- 兩份資訊都是空字串
- 輸出：`ℹ️ 資訊不足，跳過 AI 可讀性檢查`

### 情景 5：需求描述過於簡短

- commit message：`fix`
- session：`wip`
- 萃取不出任何關鍵字
- 輸出：`ℹ️ 資訊不足，跳過 AI 可讀性檢查`
