# エージェント設計パターン

## 基本テンプレート

### ユーザー向けエージェント（オーケストレーター）

```markdown
---
description: "Use when: <trigger words>. <one-line purpose>."
tools: [read, edit, search, agent, todo]
model: "Claude Sonnet 4.5 (copilot)"
argument-hint: "<入力のヒント>"
---

# <Agent Name>

あなたは<役割>の専門エージェントです。

## ミッション
<一文で目的を述べる>

## フロー
### Phase 1: <フェーズ名>
<具体的な手順>

### Phase 2: <フェーズ名>
<具体的な手順>

## 成果物
<期待するアウトプット>

## 制約
- DO NOT <禁止事項1>
- DO NOT <禁止事項2>
```

### サブエージェント（ワーカー）

```markdown
---
description: "Use when: <trigger>. Invoked by <parent-agent>."
tools: [<minimal set>]
user-invocable: false
---

# <Agent Name>

## 役割
<一文>

## 手順
1. <ステップ1>
2. <ステップ2>

## 出力フォーマット
<構造化されたアウトプット形式>

## 制約
- DO NOT <禁止事項>
```

---

## ツールセット早見表

| ユースケース | 推奨ツールセット |
|-------------|----------------|
| 読み取り専用調査 | `[read, search]` |
| ファイル編集 | `[read, edit, search]` |
| コード実行が必要 | `[read, edit, search, execute]` |
| マルチエージェント指揮 | `[read, edit, search, agent, todo]` |
| Web情報収集 | `[read, search, web]` |
| 会話のみ | `[]` |

---

## 階層設計パターン

### 3層アーキテクチャ（推奨）

```
ユーザー
  └── オーケストレーター (user-invocable: true)
        ├── アナリスト    (user-invocable: false)
        └── ワーカー      (user-invocable: false)
```

### ハンドオフパターン

```yaml
# オーケストレーター側
handoffs: [analyst-agent, worker-agent]
```

---

## description の書き方

### パターン1: Use when + What
```
"Use when: refactoring TypeScript code, improving type safety, fixing type errors."
```

### パターン2: Task + Context + Trigger
```
"Generate database migration scripts from schema changes. Use when: schema diff, migration, alembic, db update."
```

### 避けるべき description
```
# NG: 曖昧
"A helpful coding assistant."
"Manages files."

# OK: 具体的
"Use when: creating API endpoints, scaffolding REST routes, Express/Fastify route generation."
```

---

## モデル選択

| 用途 | 推奨モデル |
|------|-----------|
| 高精度推論・長文生成 | `Claude Sonnet 4.5 (copilot)` |
| 高速・軽量タスク | `GPT-4o mini (copilot)` |
| コーディング特化 | `Claude Sonnet 4 (copilot)` |
| フォールバック構成 | `model: ['Claude Sonnet 4.5 (copilot)', 'GPT-4o (copilot)']` |
