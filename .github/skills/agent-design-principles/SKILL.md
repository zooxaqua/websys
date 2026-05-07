---
name: agent-design-principles
description: 'エージェント・スキル・プロンプトの設計原則とパターン集。Use when: designing agent systems, choosing between agent/skill/prompt, planning tool sets, designing multi-agent workflows, avoiding anti-patterns in agent design.'
argument-hint: '設計したいエージェントシステムの説明'
---

# Agent Design Principles

## プリミティブ選択ガイド

| 状況 | 選ぶべきプリミティブ |
|------|---------------------|
| プロジェクト全体に常時適用したいルール | Workspace Instructions |
| 特定ファイル種別に適用したいルール | File Instructions (`applyTo`) |
| 繰り返し使う単一タスクのテンプレート | Prompt |
| 複数ステップ・バンドルアセット付きのワークフロー | Skill |
| ロール特化・ツール制限のあるエージェント | Custom Agent |
| シェルコマンドで動作を強制したい | Hooks |

詳細な設計パターン:
- [エージェント設計パターン](./references/agent-patterns.md)
- [スキル設計パターン](./references/skill-patterns.md)
- [プロンプト設計パターン](./references/prompt-patterns.md)
- [フロー・ワークフロー設計](./references/flow-patterns.md)

---

## 意思決定フローチャート

```
要求を受け取ったら...
│
├─ 常に有効にしたい？
│   └─ YES → Instructions (copilot-instructions.md or *.instructions.md)
│
├─ 単一タスク・テンプレート的？
│   └─ YES → Prompt (.prompt.md)
│
├─ 複数ステップ or アセット同梱？
│   ├─ ロール特化・ツール制限が必要？
│   │   └─ YES → Custom Agent (.agent.md)
│   └─ NO → Skill (SKILL.md)
│
└─ 外部システム連携？
    └─ YES → MCP Server
```

---

## 共通設計原則

### 1. 最小権限原則（Least Privilege）
```yaml
# Bad: 全部入り
tools: [execute, read, edit, search, web, agent]

# Good: 必要なものだけ
tools: [read, search]  # 読み取り専用タスクなら
```

### 2. キーワードリッチな description
description はエージェントが「いつ自分を使うべきか」を判断する唯一の情報源。

```yaml
# Bad: 曖昧
description: "A helpful assistant"

# Good: 具体的なトリガーワード
description: "Use when: generating TypeScript types from JSON schema, converting interfaces, type scaffolding."
```

### 3. 単一責任
1 エージェント = 1 つの明確な責任。複数の責任は複数のエージェントに分割。

### 4. 検証可能な出力
エージェントの output format を明示し、受け取る側が検証できるようにする。

---

## Anti-patterns チェックリスト

- [ ] Swiss-army エージェント（何でもする1つのエージェント）になっていないか
- [ ] description が曖昧で検索トリガーがないまま終わっていないか
- [ ] SKILL.md が 500 行を超えていないか（references に分離すべき）
- [ ] `applyTo: "**"` を不用意に使っていないか（コンテキスト汚染）
- [ ] サブエージェントが `user-invocable: true` のままになっていないか
- [ ] YAML の値にコロンがあるのにクォートしていないか
- [ ] スキルの `name` がフォルダ名と不一致になっていないか
