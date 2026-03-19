# Setup

設定 soap-dev plugin 所需的權限

# Flow

1. 讀取 `~/.claude/settings.json`，在 `permissions.allow` 中確保包含以下權限（如果已存在則不重複新增），保留其他既有設定不動：

```
Read(~/.claude/plugins/**)
```

2. 告知使用者設定完成
