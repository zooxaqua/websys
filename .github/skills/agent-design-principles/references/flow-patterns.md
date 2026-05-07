# フロー・ワークフロー設計パターン

## マルチエージェントフローの基本

### 直列フロー（Sequential Pipeline）

```
Input → [Analyst] → [Designer] → [Generator] → [Validator] → Output
```

**実装例（オーケストレーター body）:**
```markdown
## フロー
1. `requirement-analyst` を呼び出して要件を整理する
2. 設計を決定する（この判断はオーケストレーターが行う）
3. `file-generator` を呼び出してファイルを生成する
4. 出力を検証して問題があれば修正する
```

---

### 並列フロー（Parallel Processing）

```
Input → [Analyst]
              ├── [Worker A] ──┐
              └── [Worker B] ──┤→ [Aggregator] → Output
```

独立したタスクを並列に処理する場合に使用。  
ただし現在の Copilot Agent は並列実行をネイティブサポートしていないため、  
連続呼び出しで代替する。

---

### 条件分岐フロー（Conditional Routing）

```
Input → [Router]
           ├─ TypeScript? → [TS Agent]
           ├─ Python?     → [Python Agent]
           └─ Other?      → [Generic Agent]
```

**実装例:**
```markdown
## フロー
1. ファイル拡張子を確認する
2. `.ts` / `.tsx` なら TypeScript 専用処理
3. `.py` なら Python 専用処理
4. その他は汎用処理
```

---

### フィードバックループ（Retry with Feedback）

```
Input → [Generator] → [Validator]
                           │
                    NG ────┘ (最大3回)
                    OK → Output
```

**実装例:**
```markdown
## フロー
1. ファイルを生成する
2. 生成結果を検証する（構文チェック、型チェック）
3. エラーがあれば修正して 2 に戻る（最大3回）
4. 3回失敗した場合はユーザーにエラーを報告する
```

---

## ハンドオフ設計

### `handoffs` フィールド
```yaml
---
description: "..."
handoffs: [specialist-agent, reviewer-agent]
---
```

ハンドオフは「このエージェントが終わったら次のエージェントに渡す」という宣言。  
オーケストレーターパターンと組み合わせると強力。

---

## フロー設計チェックリスト

- [ ] 各エージェントの入出力が明確に定義されているか
- [ ] エラー時の処理フローが明示されているか
- [ ] 無限ループ（A → B → A）が発生しない設計か
- [ ] ユーザーへの確認ポイントが適切に設定されているか
- [ ] 最終成果物の形式が明確か

---

## フロー記述のベストプラクティス

### Phase 構造（推奨）
```markdown
## フロー

### Phase 1: 情報収集
- 既存ファイルを読み込む
- 関連コードを検索する

### Phase 2: 分析・設計
- 問題を特定する
- 解決策を検討する

### Phase 3: 実装
- 変更を加える
- テストを実行する

### Phase 4: 検証
- 変更内容を確認する
- エラーがあれば修正する
```

### 短いタスクの場合（3ステップ以内）
```markdown
## 手順
1. 対象ファイルを読み込む
2. 指定箇所を修正する
3. 変更を報告する
```
