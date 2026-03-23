# Codebase 搜尋策略

## 目標

在整個專案 codebase 中搜尋與 Story 相關的現有實作，建立對專案架構和已有程式碼的充分理解，為後續的子任務拆解提供依據。

## 搜尋原則

- **從具體到抽象**：先搜尋 Story 中的具體名詞，再擴展到相關概念
- **從結構到細節**：先了解專案結構，再深入特定檔案
- **以充分為止**：不限定搜尋次數，以「能支撐子任務拆解」為完成標準

## 搜尋流程

### Phase 1：提取關鍵字

從 Story 的 summary 和 description 中提取：
- **實體名稱**：涉及的業務物件（如 User、Order、ChatRoom）
- **動作關鍵字**：需要實作的操作（如 Register、Create、Send）
- **技術關鍵字**：提到的技術元件（如 SignalR、API、Scheduler）

### Phase 2：專案結構探索

使用 Glob 了解專案整體結構：

```
# 了解頂層目錄結構
Glob: *

# 找出後端專案結構
Glob: **/*.cs （限制深度或關鍵目錄）
Glob: **/Controllers/**
Glob: **/Services/**

# 找出前端專案結構
Glob: **/src/**/*.vue
Glob: **/src/**/*.ts
Glob: **/src/api/**
```

目的是建立對專案目錄慣例的認知，後續搜尋才能精準定位。

### Phase 3：關鍵字搜尋

使用 Grep 搜尋 Phase 1 提取的關鍵字：

```
# 搜尋實體名稱，找出相關的 Model、Controller、Service、Component
Grep: <實體名稱> （在 *.cs, *.vue, *.ts 中搜尋）

# 搜尋 API 路由，了解現有端點
Grep: [Route] 或 [Http] 搭配關鍵字

# 搜尋前端 API 呼叫
Grep: api/ 搭配關鍵字
```

### Phase 4：相似功能定位

根據 Story 的功能需求，尋找專案中已存在的相似功能：

- 如果 Story 是「新增 XX 管理」，搜尋現有的其他「管理」功能作為參照
- 如果 Story 涉及 CRUD，找出現有的 CRUD 實作模式
- 如果涉及排程，找出現有的 Coravel 排程範例

這些相似功能會成為子任務 description 中的「參考檔案」。

### Phase 5：依賴確認

針對 Phase 3/4 找到的核心檔案，進一步搜尋它們的依賴：

```
# 搜尋共用的 Service、Repository、Composable
Grep: using/import 語句中的關鍵類別名

# 搜尋介面定義
Grep: interface I<ServiceName>
```

## 搜尋結果整理

搜尋完成後，將發現整理為：

1. **現有相關檔案**：與 Story 直接相關的現有程式碼（將成為依賴檔案）
2. **相似功能範例**：可作為實作參照的現有功能（將成為參考檔案）
3. **專案慣例**：檔案命名、目錄結構、程式碼風格等慣例（用於預估新檔案路徑）
4. **影響範圍**：可能需要修改的現有檔案
