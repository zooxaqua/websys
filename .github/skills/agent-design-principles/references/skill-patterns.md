# スキル設計パターン

## 基本テンプレート

```markdown
---
name: skill-name              # lowercase-hyphen、フォルダ名と完全一致
description: 'Use when: <ユースケース>. <トリガーワード1>, <トリガーワード2>.'
argument-hint: '<スラッシュコマンドのヒント>'
user-invocable: true
---

# Skill Title

## いつ使うか
- <ユースケース1>
- <ユースケース2>

## 手順
1. <ステップ1>
2. <ステップ2>
3. 詳細は [参照ドキュメント](./references/detail.md) を参照

## 出力
<期待する成果物>
```

---

## ディレクトリ構成パターン

### シンプル（参照なし）
```
.github/skills/my-skill/
└── SKILL.md
```

### 標準（参照あり）
```
.github/skills/my-skill/
├── SKILL.md
└── references/
    ├── patterns.md
    └── examples.md
```

### フル構成
```
.github/skills/my-skill/
├── SKILL.md
├── scripts/
│   └── generate.sh
├── references/
│   ├── patterns.md
│   └── api-reference.md
└── assets/
    └── template.md
```

---

## プログレッシブローディング

スキルは3段階でロードされる:

```
1. Discovery (~100 tokens)
   └── name + description だけ読まれる
       → ここで選ばれなければ終わり

2. Instructions (<5000 tokens)
   └── SKILL.md の body が読まれる
       → 手順・ガイダンスを記述する場所

3. Resources (on-demand)
   └── body 内でリンクされたファイルだけロード
       → 詳細は references/ に分離
```

**実装指針:**
- SKILL.md の body は 500 行以内に保つ
- 詳細情報は `./references/` に分離して参照リンクを張る
- スクリプトは `./scripts/` に分離

---

## description の最適化

### 文字数目安
- 最小: 50文字（トリガーワードが見つからない）
- 推奨: 200〜500文字
- 上限: 1024文字

### 含めるべき情報
1. **何をするスキルか**（動詞+名詞）
2. **いつ使うか**（ユースケース・状況）
3. **トリガーワード**（ユーザーが言いそうなキーワード）

```
# 例:
'TypeScript プロジェクトのテストを生成するスキル。
Use when: writing unit tests, generating test cases, Jest, Vitest, test coverage,
テスト生成, ユニットテスト作成.'
```

---

## 自動 vs 手動呼び出し制御

```yaml
# デフォルト: スラッシュコマンドあり + 自動検出あり
user-invocable: true
# disable-model-invocation: false (デフォルト)

# スラッシュなし + 自動検出のみ
user-invocable: false

# スラッシュあり + 自動検出なし（明示的に呼ぶ場合のみ）
disable-model-invocation: true

# 完全手動（両方 false/true にする）
user-invocable: false
disable-model-invocation: true
```
