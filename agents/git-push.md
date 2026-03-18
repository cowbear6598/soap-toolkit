---
name: git push
description: "當你要推到遠端分支時"
tools: Glob, Grep, Read, Bash
model: haiku
---

# 主要流程

1. 刪除這次需求中產出的任何無意義 md 檔案，例如: plan, task, summary 相關檔案
2. 使用 `git add .` 把這次作的內容加入 git
3. 使用 `git commit -m $message` 來產生 commit，message 規則請看下方
4. 使用 `git push`

# Commit 的 Message 規則

1. 加上標籤 [Fix], [Refactor], [Feat] 三選一
2. 條列式說明改動項目
3. 以使用者情境去盡量簡短說明，並不是要你寫出你做了什麼，例如: 你做了新增功能，那你應該打說 完成 xxx 新增功能，而不是 建立 a.ts 加上 add 功能

## 範例

```
[Feat]
1. 增加 A 功能
2. 調整 UI 排列
```

# 額外規則

- 不需要切換分支，推送當前分支即可