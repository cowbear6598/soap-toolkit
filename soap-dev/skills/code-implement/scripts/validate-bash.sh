#!/bin/bash

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.input.command // empty')

if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# === Freeze 級 ===
FREEZE_PATTERNS=(
  'rm -rf /'
  'rm -rf ~'
  'DROP TABLE'
  'DROP DATABASE'
  'chmod 777'
)

for pattern in "${FREEZE_PATTERNS[@]}"; do
  if [[ "$COMMAND" == *"$pattern"* ]]; then
    echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"🚫 [FREEZE] Blocked: $pattern\"}}"
    exit 2
  fi
done

# === Careful 級 ===
if [[ "$COMMAND" == *"git push --force"* ]] || [[ "$COMMAND" == *"git push -f"* ]]; then
  echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"⚠️ [CAREFUL] Blocked: git push --force/-f — 如果確定要執行，請手動操作\"}}"
  exit 2
fi

if [[ "$COMMAND" == *"git reset --hard"* ]]; then
  echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"⚠️ [CAREFUL] Blocked: git reset --hard — 如果確定要執行，請手動操作\"}}"
  exit 2
fi

if [[ "$COMMAND" == *"git clean -fd"* ]]; then
  echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"⚠️ [CAREFUL] Blocked: git clean -fd — 如果確定要執行，請手動操作\"}}"
  exit 2
fi

if [[ "$COMMAND" == *"kubectl delete"* ]]; then
  echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"⚠️ [CAREFUL] Blocked: kubectl delete — 如果確定要執行，請手動操作\"}}"
  exit 2
fi

if [[ "$COMMAND" == *"npm publish"* ]]; then
  echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"⚠️ [CAREFUL] Blocked: npm publish — 如果確定要執行，請手動操作\"}}"
  exit 2
fi

if [[ "$COMMAND" == *"npx publish"* ]]; then
  echo "{\"hookSpecificOutput\":{\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"⚠️ [CAREFUL] Blocked: npx publish — 如果確定要執行，請手動操作\"}}"
  exit 2
fi

# 放行
exit 0
