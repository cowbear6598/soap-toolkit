#!/bin/bash
input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // empty')

if [[ -z "$file" || ! -f "$file" ]]; then
  exit 0
fi

dir=$(dirname "$file")

while [[ "$dir" != "/" ]]; do
  # Prettier
  if [[ -f "$dir/.prettierrc" || -f "$dir/.prettierrc.json" || -f "$dir/package.json" ]]; then
    case "$file" in
      *.vue|*.ts|*.js|*.tsx|*.jsx|*.css|*.json|*.html)
        npx --prefix "$dir" prettier --write "$file" 2>/dev/null
        exit 0 ;;
    esac
  fi

  # Go
  if [[ -f "$dir/go.mod" && "$file" == *.go ]]; then
    gofmt -w "$file" 2>/dev/null
    exit 0
  fi

  # .NET
  if ls "$dir"/*.csproj "$dir"/*.sln 2>/dev/null | head -1 > /dev/null && [[ "$file" == *.cs ]]; then
    dotnet format "$dir" --include "$file" 2>/dev/null
    exit 0
  fi

  dir=$(dirname "$dir")
done

exit 0
