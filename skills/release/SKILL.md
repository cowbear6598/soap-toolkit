---
name: release
description: "執行版本發布流程，收集 git log 整理成 CHANGELOG 並發布新版本。當使用者提到 release、發布、發版、出版本、或提供版本號想要發布時觸發。"
---

## 參數

- 使用者需提供目標版本號（例如 `0.1.1`）
- 如果沒有提供版本號，報錯並提示用法：`/release <版本號>`

## 流程

不需要詢問使用者確認，直接按順序執行。

### Step 1：收集 Commit 訊息

1. 使用 `git describe --tags --abbrev=0` 取得上一個版本 tag
2. 使用 `git log {上一個tag}..HEAD --oneline` 收集所有 commit 訊息

### Step 2：整理 CHANGELOG

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

### Step 4：更新 CHANGELOG.md

將整理好的 CHANGELOG 內容插入到 `CHANGELOG.md` 最上方（在 `# Changelog` 之後、現有版本之前），日期使用今天的日期。

### Step 5：發布

偵測專案類型，執行對應的 release 指令：
- 找到 `package.json` → 檢查 scripts 中是否有 `release` 指令，有的話執行（如 `bun run release <type>` 或 `npm run release <type>`）
- 找到 `*.csproj` → 更新 `<Version>` 標籤，commit 並打 git tag
- 其他 → 直接 commit CHANGELOG 變更，打 git tag `v{版本號}` 並 push tag
