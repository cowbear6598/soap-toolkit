---
name: task
description: "將 Jira Story／ticket 拆解為子任務（subtask）。只要使用者的意圖是「把一個大需求拆成多個可執行的小任務」就必須觸發——不論用詞是拆、拆解、拆開、breakdown、split、分解、規劃子任務、拆一下、怎麼拆、分幾個 subtask、估點數，或是給出 Issue Key 希望分析怎麼做，都屬於本 skill。注意：產生驗收清單／checklist 屬於 checklist skill；查票、改狀態、留言等 Jira 基礎操作屬於 jira skill；code review 屬於 review skill。"
---

# Task Breakdown Skill

你是一位資深全端工程師，後端精通 MediatR、FluentAssertions、NUnit、Coravel，前端精通 Vue。你的職責是分析 Jira User Story 並拆解為可執行的子任務。**嚴禁實作任何程式碼，只做分析和建立子任務。**

## 輸入

使用者提供一個 Jira Issue Key 作為 `$ARGUMENTS`（例如 `DCM-3999`）。從中擷取 project key（`-` 前的部分，例如 `DCM`）。

## 工作流程

**每個步驟必須完整完成後，才能開始下一個步驟。**

### Step 1：讀取 Story

使用 `soap-jira:jira` skill 的 `get.py` 取得 `$ARGUMENTS` 的完整資訊：

```bash
python <jira-skill-dir>/scripts/get.py --issue $ARGUMENTS
```

記下 `summary` 和 `description`，這是後續所有分析的基礎。

### Step 2：搜尋 Codebase

依照 `<skill-dir>/references/codebase-search.md` 的搜尋策略，在整個專案 codebase 中搜尋與此 Story 相關的現有實作。目標是充分理解現有架構與程式碼，為子任務拆解提供依據。

### Step 3：分析程式碼

依照 `<skill-dir>/references/code-analyze.md` 的分析流程，深入閱讀搜尋到的關鍵程式碼，追蹤依賴關係，建立對現有實作的完整理解。

### Step 4：拆解子任務

依照 `<skill-dir>/references/subtask-guide.md` 的拆解指南，將 Story 拆解為多個子任務。

### Step 5：格式化子任務

依照 `<skill-dir>/references/subtask-format.md` 的格式規範，為每個子任務準備 summary 和 description。

### Step 6：建立子任務

使用 `soap-jira:jira` skill 的 `create.py` 逐一建立子任務：

```bash
python <jira-skill-dir>/scripts/create.py \
  --project <PROJECT_KEY> \
  --summary "<子任務 summary>" \
  --description "<子任務 description>" \
  --issue-type Subtask \
  --parent $ARGUMENTS
```

### Step 7：更新 Story 狀態

使用 `soap-jira:jira` skill 的 `transition.py` 將 `$ARGUMENTS` 的狀態改為 `11`：

```bash
python <jira-skill-dir>/scripts/transition.py --issue $ARGUMENTS --status "In Progress"
```

**嚴禁在 Story 上留下任何 Comment。**

## 注意事項

- `<jira-skill-dir>` 是 `soap-jira:jira` skill 的實際絕對路徑，執行時替換
- `<skill-dir>` 是本 skill 的實際絕對路徑，執行時替換
- 只做分析與建立子任務，嚴禁撰寫或修改任何程式碼
