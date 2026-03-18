# Main Quest

- 收集上一版本到目前為止的 git log，整理成 CHANGELOG 內容，直接執行 release 流程

# 參數

- $ARGUMENTS 為目標版本號（例如 `0.1.1`）
- 如果沒有提供版本號，報錯並提示用法：`/release <版本號>`

# Flow

- 遵循此 Flow 順序一步一步往下做，不需要詢問使用者確認

1. 使用 `git describe --tags --abbrev=0` 取得上一個版本 tag，然後用 `git log {上一個tag}..HEAD --oneline` 收集所有 commit 訊息
2. 將 commit 訊息按照分類規則整理為 CHANGELOG 區塊
3. 根據目標版本號和當前版本號判斷 release type（major/minor/patch）
4. 將整理好的 CHANGELOG 內容插入到 `CHANGELOG.md` 最上方（在 `# Changelog` 之後、現有版本之前），日期使用今天的日期
5. 執行 `bun run release <type>` 完成發布

# Release Type 判斷規則

- 比較目標版本號和當前版本號（從 `package.json` 讀取）
- major 變了 → `major`
- minor 變了 → `minor`
- patch 變了 → `patch`

# CHANGELOG 分類規則

- commit message 開頭為 `[Feat]` 或包含「新增」→ 歸類為「新增」
- commit message 開頭為 `[Fix]` 或包含「修復」「修正」→ 歸類為「修正」
- commit message 開頭為 `[Refactor]` 或包含「重構」→ 歸類為「重構」
- commit message 開頭為 `[Release]` → 跳過不列入
- 其他 → 歸類為「其他」
- 空的分類不要顯示

# CHANGELOG 內容整理規則

- **精簡描述**：不要照搬 commit message，提煉成一句話重點。例如 commit 寫了「增加 MCP Server 支援 1. 後端：新增 MCP Server 類型... 2. 前端：...」，CHANGELOG 只需寫「新增 MCP Server 支援」
- **拆分多主題**：如果一個 commit 包含多個獨立功能/改動，拆成多條 CHANGELOG 條目。例如 commit 同時做了「MCP Server 支援」和「Claude Service 整合」，應拆為兩條
- **合併同主題**：多個 commit 改的是同一件事（例如連續修 install.sh 換行符問題），合併為一條。例如「修正 install.sh 換行符問題」
- **跳過模糊 commit**：commit message 沒有明確描述具體改了什麼的直接跳過不列入（例如「Code review 修正改動」、「修正一些問題」這類模糊描述）

# CHANGELOG 格式範例

```markdown
## [x.x.x] - yyyy-mm-dd

### 新增
- 某某功能

### 修正
- 某某 bug

### 重構
- 某某重構
```
