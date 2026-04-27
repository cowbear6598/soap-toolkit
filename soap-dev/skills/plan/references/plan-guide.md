# 計畫書撰寫規則

## 核心原則

- 拿到這份計畫書的人應該能直接按步驟實作，無需額外猜測
- 不需要做無謂的向後相容，造成程式碼的後期負擔
- 不要用程式碼來描述工作內容，以免計畫書過長以及過度工程化

## 撰寫流程

1. 閱讀 user flow 了解使用情境
2. 先根據 user flow 列出要做哪些測試案例（只需定義名稱）
3. 撰寫實作計畫
4. 最後撰寫測試內容

## 顆粒度要求

- 每個 Todo 項目必須是**可直接執行的具體步驟**
- 如需欄位描述請詳細填寫
- 不要用程式碼描述工作內容

## Fallback / Defensive Code 防護規則

使用者的工作流是「只看 plan 的情境章節，不細看 todo」。Fallback / defensive code 若藏在 todo 細節裡，會躲過審查，最後變成程式中一堆沒必要的防衛分支與配套的邊界測試。

**規則**：產出計畫書時，只要 todo 出現以下任何一種情況，**必須先用 AskUserQuestion 與使用者逐一對齊每一項的必要性，對齊通過後才能寫入 todo**：

- try-catch 包覆（例外：第三方服務呼叫、I/O、網路請求這類「真實會失敗的邊界」可直接寫入）
- null / undefined / 空值的 fallback（例如 `value ?? default`、`if (!x) return [...]`）
- 預設值兜底（找不到資料時回傳預設值）
- 重試邏輯 retry / backoff
- TypeScript 型別系統已保證的防衛（例如已宣告為 `string` 還寫 `if (typeof x !== 'string')`）

**對齊問題格式建議**：每一個 fallback 都要列出
1. 該 fallback 是什麼（出現在哪個情境 / 哪個函式）
2. 不加會發生什麼後果
3. 建議是否需要（並說明理由）

**規則精神**：用 AskUserQuestion 對齊 fallback 時，「不加會發生什麼後果」必須**從正規使用路徑反推**。

- ✅ 允許的論證：「正規 UI 流程下 X 會發生 → 需要處理」
- ❌ 禁止的論證：用假設性 client（「如果有 CLI 會...」）、假設性威脅（「萬一有人直連 WS...」）、想像中的測試工具當理由 — 除非系統實際存在這些 client。

判定流程：
1. 從正規使用路徑可達？→ 否 → 不需要 fallback（不要列入對齊問題）
2. 可達 → 列入對齊問題，論證限定在實際路徑

讓使用者明確點頭後才能進入 todo，否則寧可不寫，事後讓錯誤自然浮現。

## Phase 分組規則

- 計畫書必須用 Phase 來分組（`### Phase 1`、`### Phase 2`...）
- 每個 Phase 是一個執行批次
- 同一個 Phase 內的大項目「可以並行」執行，此時標題加註「可並行」（例如 `### Phase 2（可並行）`）
- 不同 Phase 之間必須「依序」執行（Phase 1 全部完成才能做 Phase 2）
- 如果該 Phase 內只有一個大項目，或者雖然有多個但它們之間有依賴，就不要標「可並行」
- 只有確定沒有互相依賴的大項目才放在同一個 Phase

## 大項目結構規則

- 每個 Phase 內的大項目用字母編號：A. B. C. ...
- 每個 Phase 內的編號從 A 重新開始
- 大項目下面才是具體的 Todo（checkbox 格式）
- 大項目名稱要簡短明確，一看就知道這個區塊在做什麼

## 輸出位置

- 前端：`tasks/frontend.md`
- 後端：`tasks/backend.md`

## 範例

### 後端

```markdown
### Phase 1（可並行）

A. 建立 Order 模型與資料庫
  - [ ] 建立 `Order.cs` Entity
  - [ ] 建立 `CreateOrderRequest.cs`
    - 包含屬性：`UserId`, `ProductId`, `Quantity`, `TotalPrice`
    - 加上驗證標註：`[Required]`, `[Range(1, 999)]`
  - [ ] 新增 Migration

B. 建立 Notification 服務
  - [ ] 建立 `NotificationService.cs`
  - [ ] 實作 `SendOrderNotification` 方法

### Phase 2

A. 實作 Order API
  - [ ] 在 `OrdersController.cs` 新增 `CreateOrder`
  - [ ] 實作 `OrderService.CreateAsync`
  - [ ] 測試訂單建立與取消流程
```

### 前端

```markdown
### Phase 1

A. API 服務層
  - [ ] 建立 `orderApi.ts`
  - [ ] 實作 `createOrder()` 和 `getOrders()`

### Phase 2（可並行）

A. 訂單列表頁
  - [ ] 建立 `OrderList.vue`
  - [ ] 實作 `fetchOrders()` 方法

B. 訂單詳情頁
  - [ ] 建立 `OrderDetail.vue`
```
