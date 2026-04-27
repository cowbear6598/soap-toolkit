---
name: release
description: "執行版本發布流程，收集 git log 整理成 CHANGELOG 並發布新版本。當使用者提到 release、發布、發版、出版本、或提供版本號想要發布時觸發。"
---

## 參數

- 使用者需提供目標版本號（例如 `0.1.1`）
- 如果沒有提供版本號，報錯並提示用法：`/release <版本號>`

## 使用方式

使用 Agent tool，不指定 subagent_type（通用 agent），model 設為 haiku。

將以下流程和參數一起傳入 agent 的 prompt。

## 流程

不需要詢問使用者確認，直接按順序執行。

### Step 1：派 sub-agent 蒐集 commits（強制）

不要在主對話直接跑 `git log` 收集 commits — 會偷懶漏抓。改用 Agent tool 啟動一個 general-purpose sub-agent，明確指示它：

1. 跑 `git describe --tags --abbrev=0` 取得上一版 tag（記為 `PREV_TAG`）
2. 跑 `git log {PREV_TAG}..HEAD --pretty=format:'%h %s'` 列出所有 commits
3. 對每個 commit 依其 message prefix 建議分類（Feat / Fix / Refactor / Docs / Chore / 其他）
4. 回傳結構化清單，格式為：
   ```
   PREV_TAG: vX.Y.Z
   Total commits: N

   1. {hash} [{分類}] {message}
   2. {hash} [{分類}] {message}
   ...
   ```

sub-agent 回報後，主流程必須把 `Total commits: N` 這個數字記下來，進入 Step 2 時用於對帳。

### Step 2：整理 CHANGELOG

**對帳檢查（強制）**

在開始寫 CHANGELOG 之前，先聲明：
> sub-agent 回報共 N 條 commits，CHANGELOG 條目數應 ≥ N - 合併數（多個相關 commit 可合併為一條）。

CHANGELOG 草稿完成後，再次自我檢查：條目總數是否符合上述對帳要求？若明顯少於 N，必須回頭補齊。

將 commit 訊息按照分類規則整理為 CHANGELOG 區塊。

**分類規則：**
- `[Feat]` 或包含「新增」→ 歸類為「新增」
- `[Fix]` 或包含「修復」「修正」→ 歸類為「修正」
- `[Release]` → 跳過不列入
- 其他 → 全部歸入「新增」或「修正」中最適合的分類
- 空的分類不要顯示

**整理規則：**
- 精簡描述：不要照搬 commit message，提煉成一句話重點
- 拆分多主題：一個 commit 包含多個獨立功能，拆成多條
- 合併同主題：多個 commit 改同一件事，合併為一條
- 跳過模糊 commit：message 沒有明確描述的直接跳過（例如「修正一些問題」）

**格式：**

```markdown
## [x.x.x] - yyyy-mm-dd

### 新增
- 某某功能

### 修正
- 某某 bug
```

### Step 3：判斷 Release Type

偵測當前版本號的來源，比較目標版本號和當前版本號：
- 找到 `package.json` → 從 `version` 欄位讀取
- 找到 `*.csproj` → 從 `<Version>` 標籤讀取
- 找到 `go.mod` → 從最近的 git tag 讀取
- 其他 → 從最近的 git tag 讀取

比較結果：
- major 變了 → `major`
- minor 變了 → `minor`
- patch 變了 → `patch`

### Step 4：更新版本號

搜尋專案中所有含有 version 欄位的設定檔（如 package.json、plugin.json、*.csproj 等），將版本號更新為目標版本號。

### Step 5：更新 CHANGELOG.md

將整理好的 CHANGELOG 內容插入到 `CHANGELOG.md` 最上方（在 `# Changelog` 之後、現有版本之前），日期使用今天的日期。

### Step 6：發布

偵測專案類型，執行對應的 release 指令：
- 找到 `package.json` → 檢查 scripts 中是否有 `release` 指令，有的話執行（如 `bun run release <type>` 或 `npm run release <type>`）
- 找到 `*.csproj` → 更新 `<Version>` 標籤，commit 並打 git tag
- 其他 → 直接 commit CHANGELOG 變更，打 git tag `v{版本號}` 並 push tag
