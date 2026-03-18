# Install Statusline

將 soap-dev 的自訂 statusline 安裝到 Claude Code

# Flow

1. 使用 Bash 將 `${CLAUDE_PLUGIN_ROOT}/statusline/statusline.sh` 和 `${CLAUDE_PLUGIN_ROOT}/statusline/calc-monthly-cost.py` 複製到 `~/.claude/statusline/`，如果目錄不存在則建立
2. 確保 `statusline.sh` 有執行權限
3. 讀取 `~/.claude/settings.json`，將 `statusline` 欄位設定為 `~/.claude/statusline/statusline.sh`，保留其他既有設定不動
4. 完成後告知使用者重啟 Claude Code 即可生效
