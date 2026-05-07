# プロンプト設計パターン

## 基本テンプレート

```markdown
---
description: "<このプロンプトの用途を一文で>"
agent: "agent"
tools: [read, edit, search]
---

<タスクの指示>

## 入力
${input}

## 期待する出力
<フォーマット例>
```

---

## `agent` フィールドの選択

| 値 | 効果 |
|----|------|
| `"ask"` | Copilot Chat の通常モード（会話のみ） |
| `"agent"` | Agent モード（ツール使用可） |
| `"plan"` | 計画モード（実行前に確認） |
| カスタムエージェント名 | 特定エージェントで実行 |

---

## パラメータの使い方

### `${変数名}` パターン
```markdown
---
description: "指定クラスの単体テストを生成する"
agent: "agent"
---

`${targetClass}` クラスの単体テストを生成してください。

要件:
- フレームワーク: ${testFramework:Jest}
- カバレッジ目標: ${coverage:80}%
- モック戦略: ${mockStrategy:manual}
```

### コンテキスト参照
```markdown
[設定ファイル](./config.json) の仕様に従って実装してください。
```

---

## ユースケース別パターン

### コード生成プロンプト
```markdown
---
description: "${language} のボイラープレートを生成する"
agent: "agent"
tools: [edit]
---

以下の仕様で ${language} のコードを生成してください:
- 仕様: ${spec}
- スタイル: [既存コードのパターンを踏襲する]
- テスト: [生成後にテストも作成する]
```

### レビュープロンプト
```markdown
---
description: "コードレビューチェックリストを実行する"
agent: "agent"
tools: [read, search]
---

以下の観点でコードをレビューしてください:
1. セキュリティ（OWASP Top 10）
2. パフォーマンス
3. 可読性
4. テストカバレッジ
```

### ドキュメント生成プロンプト
```markdown
---
description: "README または API ドキュメントを生成する"
agent: "agent"
tools: [read, edit, search]
---

プロジェクトの構成を調査し、以下を含む ${docType} を生成してください:
- 概要
- インストール手順
- 使い方
- API リファレンス（該当する場合）
```

---

## Anti-patterns

```markdown
# NG: 複数タスクを1プロンプトに詰め込む
"コードを書いて、テストして、デプロイして、ドキュメントも書いて"

# OK: 単一タスクに分割
"指定された仕様からコードを生成する" (別プロンプト)
"生成されたコードのテストを実行する" (別プロンプト)
```

---

## prompts/ ディレクトリ構成例

```
.github/prompts/
├── new-feature.prompt.md       # 新機能の実装
├── code-review.prompt.md       # コードレビュー
├── generate-tests.prompt.md    # テスト生成
├── create-docs.prompt.md       # ドキュメント作成
├── new-agent.prompt.md         # エージェント作成
├── new-skill.prompt.md         # スキル作成
└── new-prompt.prompt.md        # プロンプト作成
```
