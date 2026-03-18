# Install Hooks

將 soap-dev 的 hooks 安裝到 Claude Code

# Flow

1. 使用 Bash 將 `${CLAUDE_PLUGIN_ROOT}/hooks/format-on-save.sh` 複製到 `~/.claude/hooks/`，如果目錄不存在則建立
2. 確保 `format-on-save.sh` 有執行權限
3. 讀取 `~/.claude/settings.json`，在 `hooks.PostToolUse` 中加入以下設定，保留其他既有設定不動：

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "~/.claude/hooks/format-on-save.sh",
      "async": true
    }
  ]
}
```

4. 如果 `hooks.PostToolUse` 已有相同 matcher 的設定，則更新而非重複新增
