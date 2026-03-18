# Main Quest

- 根據 $1 的需求，來按以下步驟去執行，最終產生一份 plan 實作計畫書

# Flow

- 遵循此 Flow 順序一步一步往下做

1. 使用 explore agent 來搜尋 codebase 取得目前程式碼的關聯，可以一次開啟多個 agent 幫你找出資訊
2. 請盡量用 AskUserQuestion 提問使用者各種細節與情境，來減少彼此之間的誤差
3. 啟動 user-flow-definer agent 來產出使用者情境
4. 同時啟動 mermaid-creator、 plan-backend、 plan-frontend agnet 並帶入對應的 skill 與 user flow 來產出計劃書
5. 彙整計劃書資訊，確保計劃書資訊是一致以及跟你理解上的是一樣的，如果有疑慮要發問，如果有不一致的地方請修改計畫書，尤其是對於 Request/Response 資料傳輸的部分
6. 啟動 implement agent 並帶入對應的 skill 以及足夠的 context 開始實作計畫書內容，可以一次啟動多個 agent 實作，只需要補足資訊即可