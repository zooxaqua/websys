---
description: "新しいカスタムエージェント (.agent.md) を単体で作成するテンプレート"
agent: "agent"
tools: [read, edit, search]
argument-hint: "作成するエージェントの目的と名前"
---

# New Agent

`.github/agents/` に新しいカスタムエージェントを作成します。

## 入力情報

- **エージェント名**: ${agentName}
- **目的**: ${purpose}
- **ツール要件**: ${tools:自動で判断}
- **サブエージェントとして使う**: ${isSubagent:no}

---

## 作成手順

1. 以下のテンプレートを `.github/agents/${agentName}.agent.md` に作成する

```markdown
---
description: "Use when: ${triggerKeywords}. ${purpose}."
tools: [${tools}]
${isSubagent == "yes" ? "user-invocable: false" : ""}
---

# ${agentName}

## 役割
${purpose}

## 手順
1. <ステップ1>
2. <ステップ2>
3. <ステップ3>

## 出力フォーマット
<期待するアウトプット>

## 制約
- DO NOT <禁止事項>
```

2. frontmatter の YAML 構文を検証する（コロンを含む値はクォート）
3. description にトリガーワードが十分含まれているか確認する
4. 作成したファイルパスと使い方を報告する
