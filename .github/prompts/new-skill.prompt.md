---
description: "新しいスキル (SKILL.md) を作成するテンプレート。スキル名・目的・手順からスキルファイル一式を生成する"
agent: "agent"
tools: [read, edit]
argument-hint: "作成するスキルの名前と目的"
---

# New Skill

`.github/skills/<name>/SKILL.md` を含むスキル一式を作成します。

## 入力情報

- **スキル名 (slug)**: ${skillName}  ← `lowercase-hyphen` 形式
- **目的**: ${purpose}
- **ユースケース**: ${useCases}
- **参照ファイルが必要**: ${needsReferences:yes}

---

## 作成手順

### 1. SKILL.md を作成

`.github/skills/${skillName}/SKILL.md` を下記フォーマットで作成する:

```markdown
---
name: ${skillName}
description: 'Use when: ${useCases}. ${triggerKeywords}.'
argument-hint: '${argumentHint}'
---

# ${skillTitle}

## いつ使うか
${useCases}

## 手順
1. <ステップ1>
2. <ステップ2>
3. 詳細は [パターン集](./references/patterns.md) を参照

## 出力
<期待する成果物>
```

### 2. 参照ファイルを作成（needsReferences が yes の場合）

`.github/skills/${skillName}/references/patterns.md` に詳細情報を記述する。

### 3. 検証

- [ ] `name` フィールドがフォルダ名 `${skillName}` と一致しているか
- [ ] description がシングルクォートで囲まれているか
- [ ] SKILL.md が 500 行以内か

作成したファイル一覧を報告する。
