# Install Style Conductor

將 soap-dev 的 conductor output style 安裝到 Claude Code

# Flow

1. 使用 Bash 將 `${CLAUDE_PLUGIN_ROOT}/output-styles/conductor.md` 複製到 `~/.claude/output-styles/conductor.md`，如果目錄不存在則建立
2. 告知使用者安裝完成，需要重新啟動 Claude Code 才會生效，届時可以透過 `/config` 切換到 conductor output style
