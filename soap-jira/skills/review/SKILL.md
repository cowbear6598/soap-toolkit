---
name: review
description: 手動觸發
---

# TODO LIST

- **每個步驟必須完整完成並標記 completed 後，才能開始下一個步驟，沒有到達該步驟時，嚴禁閱讀任何步驟中提到的檔案**

1. 使用 `git --no-pager log --since="2 weeks ago" --grep="$ARGUMENTS" --name-status` 取得有 A,M 的程式碼
2. 將取得的檔案使用 `soap-dev:review` skill 進行 review
3. 將 review 結果嚴格轉換成以下格式：
```markdown
======================= Quality =======================
`xxxxxx.cs` - Quality - 🔴 - xxxxxxxxxxxx 原因 - 建議使用 xxxxxx

======================= Complex =======================
`sssssssss.ts` - complex - 🟡 - xxxxxxxxxxxxxx 原因 - 建議使用 xxxxxxx 簡化

======================= Style =======================
`aaaaaaaaa.vue` - Style - 🟢 - xxxxxxxxxx 原因
```
4. 使用 jira skill 發送整理後的結果到該則 issue 的 comment，並把該 issue 的狀態改成 `RD Code Review`
