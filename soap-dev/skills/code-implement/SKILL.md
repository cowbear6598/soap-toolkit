---
name: code-implement
description: "根據計畫書實作程式碼。當使用者說「開始實作」「按照計畫做」「implement」「開工」或想把計畫書轉為實際程式碼時觸發。"
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "${CLAUDE_SKILL_DIR}/scripts/validate-bash.sh"
          timeout: 10
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "${CLAUDE_SKILL_DIR}/scripts/check-path.sh"
          timeout: 10
---

## 使用方式

使用 Agent tool，不指定 subagent_type（通用 agent），model 設為 sonnet。

將以下規則和計畫書內容一起傳入 agent 的 prompt。

## 實作規則

### 實作前

- 善用搜尋工具了解程式碼的依賴關係和既有架構
- 計畫書提供方向，但實作時一定會遇到計畫書沒提到的細節，所以要自己確認再動手
- 不要盲目照抄計畫書，如果發現計畫書有不合理的地方，以實際 codebase 為準

### 實作中

- 不要產出任何 summary、plan、task 等無用的 markdown 檔案
- 專注在寫程式碼，不是寫文件

### 實作後

- 偵測專案類型，執行對應的測試指令：
  - 找到 `*.csproj` → `dotnet test`
  - 找到 `package.json` → 看 scripts 裡的 test 指令（`npm test` / `bun test` 等）
  - 找到 `go.mod` → `go test ./...`
  - 其他 → 搜尋 codebase 中的測試設定檔來判斷
- 所有測試通過才算完成
- 測試失敗就修，修完再跑，直到全部通過
