---
name: threads
description: 取得 Threads 公開使用者的最新貼文、文字、媒體與互動資訊。當使用者提供 Threads URL、帳號，或要求查看、抓取、分析、整理某人的 Threads 公開內容時使用。
---

# Threads

```bash
python3 <skill-dir>/scripts/fetch.py --user username --count 20
```

將 profile URL、`@username` 或 username 正規化成不含 `@` 的值。公開 SSR 通常最多提供約 15 篇，即使 `--count` 預設為 20。

腳本輸出貼文文字、時間、媒體 URL、likes 與 replies 的 JSON。依使用者問題選擇呈現或分析方式。它以 Googlebot UA 解析公開 SSR HTML，不需 token，但無法取得私人內容或分頁；解析失敗時不要推論成沒有貼文。
