---
name: checklist
description: "根據 Jira Story 產生驗收清單（acceptance checklist）。只要使用者的意圖是「列出需要驗證/測試的項目」就應觸發——包括驗收清單、checklist、測試清單、QA 清單、驗收項目、驗證項目、測試案例、acceptance criteria 整理等。注意：「拆任務／breakdown／拆 Story」是 task skill 的範疇，不是本 skill；狀態變更、留言、建票等 Jira 基礎操作屬於 jira skill。"
---

# Checklist Skill

根據 Jira User Story 及其所有子任務，分析需求後產生驗收清單，並建立為新的子任務。

## 輸入

使用者提供一個 Jira Issue Key 作為 $ARGUMENTS（例如 `DCM-3999`）。

## 工作流程

### Step 1：讀取主 Issue

使用 `soap-jira:jira` skill 執行 `get.py --issue $ARGUMENTS --include-subtasks`，取得該 Issue 的 summary、description 及子任務列表。

### Step 2：讀取所有子任務

從 Step 1 的結果中找出所有子任務（subtasks）的 issue key。逐一使用 `soap-jira:jira` skill 執行 `get.py --issue <subtask-key>` 讀取每個子任務的 summary 和 description。

### Step 3：分析與產生驗收清單

綜合 User Story 和所有子任務的內容，依照 `<skill-dir>/references/checklist-guide.md` 的指南進行分析，識別功能模組和測試範圍，產生驗收清單。

輸出格式嚴格遵循 `<skill-dir>/references/checklist-format.md`。

### Step 4：建立子任務

使用 `soap-jira:jira` skill 執行 create.py 建立新的子任務：

```
create.py --project <從 $ARGUMENTS 提取的 project key> --summary "驗收清單" --description "<產生的驗收清單內容>" --issue-type Subtask --parent $ARGUMENTS
```

Project key 從 $ARGUMENTS 中提取（例如 `DCM-3999` 的 project key 為 `DCM`）。

### Step 5：切換 Story 狀態

使用 `soap-jira:jira` skill 執行 transition.py 將原始 Story 的狀態改為 In Progress：

```
transition.py --issue $ARGUMENTS --status "In Progress"
```

### Step 6：回報結果

向使用者回報已完成，包含新建子任務的 issue key。
