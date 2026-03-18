---
name: git-push
description: "提交並推送程式碼到遠端。當使用者說「push」「推上去」「commit」「git push」或想把改動推到遠端時觸發。"
---

## 使用方式

使用 Agent tool，不指定 subagent_type（通用 agent），model 設為 haiku。

將以下規則傳入 agent 的 prompt。

## 流程

1. 刪除這次需求中產出的任何無用 md 檔案（plan、task、summary 等）
2. `git add .` 加入所有改動
3. `git commit -m $message`（格式見下方）
4. `git push`（推送當前分支，不切換分支）

## Commit Message 格式

1. 第一行加上標籤，三選一：`[Fix]`、`[Refactor]`、`[Feat]`
2. 條列式說明改動項目
3. 用使用者情境描述，不是技術描述。例如：你做了新增功能，應該寫「完成 XXX 功能」，而不是「建立 a.ts 加上 add 功能」

### 範例

```
[Feat]
1. 完成訂單建立功能
2. 調整訂單列表 UI 排列
```
