---
description: "エージェントシステム全体（agent + skill + prompt のセット）を設計・構築する"
agent: "agent-builder"
argument-hint: "作りたいエージェントシステムの説明"
---

# New Agent System

`agent-builder` を使って、エージェントシステム全体を設計・生成します。

## あなたのやりたいこと

${systemDescription}

## 構成の希望（任意）

- **エージェント数**: ${agentCount:自動で決定}
- **スコープ**: ${scope:workspace (.github/)}
- **メインユースケース**: ${useCase}

---

## agent-builder への指示

上記の要求を受けて、以下のステップで進めてください:

1. **要件ヒアリング**: 不明点がある場合は `requirement-analyst` サブエージェントで整理する
2. **設計**: 最適なプリミティブ構成（agent / skill / prompt の組み合わせ）を決定する
3. **生成**: `file-generator` で全ファイルを生成する
4. **検証**: 生成後に構文・整合性チェックを行う
5. **報告**: 作成したファイル一覧と使い方を報告する
