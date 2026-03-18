# Main Quest

- 了解改動了哪些檔案，並啟動 review agent 開始 review，最後再去檢查這些問題是否有必要修正還是誤判

# Flow

- 遵循此 Flow 順序一步一步往下做

1. 使用 `git diff --name-only` 了解目前改動哪些檔案
2. 呼叫以下 sub agent 並變成 local agent 來 review:
  - code-complex-review
  - code-security-review
  - code-style-review
  - test-case-review
  - redundant-review
3. 彙整結果由你來判斷這些問題是否誤判或者需要修正，僅有要與不要兩種選項，不能給出可修可不修這種模稜兩可的選項，同時，如果非本次修改但是一樣是值得修正的問題也需要一起了解跟修正s