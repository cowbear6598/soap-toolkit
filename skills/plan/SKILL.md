---
name: plan
description: "根據需求產出完整的實作計畫書，包含 User Flow 定義、前後端計畫。當使用者提到要做新功能、規劃、計畫、plan、設計方案、或想在動手前先想清楚怎麼做時觸發。即使使用者只說「我想做一個 XXX」或「幫我規劃一下」，只要是在談論新功能或改動的規劃，就應該使用這個 skill。"
---

## 流程

### Step 1：探索 Codebase

使用 Agent tool（Explore agent）搜尋 codebase，了解目前的程式碼架構和相關檔案。可以同時開多個 agent 平行搜尋不同面向的資訊。

### Step 2：釐清需求

用 AskUserQuestion 向使用者提問，確認以下細節：
- 具體要做什麼
- 有哪些使用情境
- 有沒有特殊限制或規格

目標是減少你和使用者之間的理解誤差。問到你確信自己完全理解需求為止。

### Step 3：定義 User Flow

讀取 `references/user-flow.md` 了解規則，然後產出使用者情境列表，儲存至 `tasks/userflow.md`。

### Step 4：平行產出計畫書

同時啟動前端和後端的計畫 agent（如果需求只涉及單邊則只啟動一個）。

每個 agent 的 prompt 需包含：
- 讀取 `references/plan-guide.md` 了解計畫書撰寫規則
- 產出的 user flow 內容
- 指定是前端還是後端
- 輸出位置：前端 → `tasks/frontend.md`，後端 → `tasks/backend.md`

### Step 5：彙整與校驗

收到所有計畫書後，檢查以下幾點：

1. **前後端一致性** — 前端呼叫的 API 和後端提供的 API 是否對得上（路由、HTTP method、Request/Response 格式）
2. **User Flow 覆蓋** — 每個 user flow 是否都有對應的實作步驟
3. **計畫書可執行性** — 拿到這份計畫書的人是否能直接按步驟實作，不需要猜

如果有不一致或遺漏，直接修改計畫書。有疑慮的地方向使用者確認。
