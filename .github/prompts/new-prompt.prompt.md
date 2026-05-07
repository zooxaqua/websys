---
description: "新しいプロンプトファイル (.prompt.md) を作成するテンプレート。単一タスクの再利用可能なプロンプトを生成する"
agent: "agent"
tools: [read, edit]
argument-hint: "プロンプトの目的と名前"
---

# New Prompt

`.github/prompts/` に新しいプロンプトファイルを作成します。

## 入力情報

- **プロンプト名**: ${promptName}  ← ファイル名（拡張子不要）
- **目的・タスク**: ${purpose}
- **実行モード**: ${agentMode:agent}  ← `ask` / `agent` / `plan`
- **必要なツール**: ${tools:自動で判断}
- **パラメータ**: ${parameters:なし}

---

## 作成手順

1. `.github/prompts/${promptName}.prompt.md` を下記フォーマットで作成する:

```markdown
---
description: "${purpose}"
agent: "${agentMode}"
tools: [${tools}]
argument-hint: "${argumentHint}"
---

# ${promptTitle}

${taskDescription}

## 入力
${parameters}

## 期待する出力
<出力フォーマットの例>

## 注意事項
- <品質要件>
- <スタイルガイドライン>
```

2. 検証:
   - [ ] 単一タスクにフォーカスしているか
   - [ ] description がユースケースを明確に説明しているか
   - [ ] パラメータ `${変数名}` の形式が正しいか

3. 作成したファイルパスとスラッシュコマンドでの呼び出し方を報告する。
