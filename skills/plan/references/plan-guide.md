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

## 輸出位置

- 前端：`tasks/frontend.md`
- 後端：`tasks/backend.md`

## 範例

### 後端

```markdown
- [ ] 建立 `OrdersIntegrationTests.cs`
  - 建立 訂單完成 的 Method
  - 建立 訂單取消 的 Method
- [ ] 建立 `CreateOrderRequest.cs` 模型
  - 包含屬性：`UserId`, `ProductId`, `Quantity`, `TotalPrice`
  - 加上驗證標註：`[Required]`, `[Range(1, 999)]`
- [ ] 在 `OrdersController.cs` 中新增 `CreateOrder` 方法
- [ ] 實作 `OrderService.CreateAsync` 方法
- [ ] 測試 `OrdersIntegrationTests.cs`
  - 測試完整的建立訂單流程
    - 準備測試資料：建立測試用戶和產品
    - 發送 POST /api/orders 請求
    - 驗證訂單被建立且庫存被扣除
  - 測試取消訂單流程
    - 建立訂單後立即取消
    - 驗證訂單狀態和庫存恢復
```

### 前端

```markdown
### API 服務層
- [ ] 建立 `orderApi.ts`
- [ ] 實作 `createOrder(request: CreateOrderRequest): Promise<Order>`

### 訂單列表頁面
- [ ] 建立 `OrderList.vue` 組件
- [ ] 實作 `fetchOrders()` 方法
```
