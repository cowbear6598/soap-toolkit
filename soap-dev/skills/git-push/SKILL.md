---
name: git-push
description: "提交並推送程式碼到遠端。當使用者說「push」「推上去」「commit」「git push」或想把改動推到遠端時觸發。"
---

## 使用方式

使用 Agent tool，不指定 subagent_type（通用 agent），model 設為 haiku。

將以下規則傳入 agent 的 prompt。

## 流程

1. 刪除這次需求中產出的任何無用 md 檔案（plan、task、summary 等）
2. 偵測專案類型，執行所有檢查指令：
   - 找到 `package.json` → 檢查 scripts 中的檢查類指令（如 `test`、`lint`、`style`、`typecheck`、`format:check` 等），全部執行
   - 找到 `*.csproj` → `dotnet test`
   - 找到 `go.mod` → `go test ./...`
   - 其他 → 搜尋 codebase 中的測試與檢查設定檔來判斷
   - 如果專案沒有任何檢查指令，跳過此步驟
3. 任一檢查失敗 → 停止流程，回報錯誤，不要 commit 也不要 push
4. 全部通過（或無檢查指令）→ 繼續：
   - `git add .` 加入所有改動
   - `git commit -m $message`（格式見下方）
   - `git push`（推送當前分支，不切換分支）

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
