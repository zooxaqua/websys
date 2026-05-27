---
name: websys-testing-standards
description: 'Webシステム開発プロジェクトのテスト規約・MCDC・カバレッジ基準。Use when: writing unit tests, integration tests, system tests, MCDC coverage, test design for websys project.'
argument-hint: 'テスト種別（unit, integration, system）またはテスト対象'
---

# Websys テスト規約

## テスト種別と基準

| 種別 | 工程 | 基準 | フレームワーク |
|------|------|------|--------------|
| 単体テスト | 工程5 | MCDC 100%・閾値テスト全件 | PHPUnit / Vitest / pytest |
| 結合テスト | 工程6 | 全連携シナリオ PASS・アプリ独立性確認 | pytest / PHPUnit |
| システムテスト | 工程7 | E2E全件・性能基準・OWASP Top 10 | Playwright / k6 |

## MCDC カバレッジ（単体テスト必達）

MCDC（Modified Condition/Decision Coverage）= 各条件が独立して決定結果を変える組み合わせを網羅。

```
例: authenticate(userExists: bool, passwordCorrect: bool)
最小テストセット:
  1. [true,  true]  → success  ← ベースケース
  2. [false, true]  → fail     ← userExists のみ変化
  3. [true,  false] → fail     ← passwordCorrect のみ変化
```

### テストケース設計テンプレート

```
テストID: TC-<モジュール>-<連番>
対象: <クラス>::<メソッド>()
条件:
  - C1: <条件1の説明>
  - C2: <条件2の説明>
MCDC 組み合わせ:
  | C1    | C2    | 期待結果 | MCDC目的 |
  |-------|-------|---------|---------|
  | true  | true  | ...     | ベース  |
  | false | true  | ...     | C1変化  |
  | true  | false | ...     | C2変化  |
境界値ケース:
  - <境界値1>: ...
  - <境界値2>: ...
```

## フレームワーク別セットアップ

詳細は各リファレンスを参照:
- [PHPUnit 設定](./references/phpunit-setup.md)
- [Vitest 設定](./references/vitest-setup.md)
- [pytest 設定](./references/pytest-setup.md)

## バグレポート形式（issue-manager への登録）

```json
{
  "type": "bug",
  "phase": 5,
  "severity": "critical | high | medium | low",
  "title": "[TC-XXX-001] <テスト名> が失敗",
  "description": "期待値: <expected>\n実際値: <actual>\n再現手順: <steps>",
  "affectedFile": "src/..."
}
```

## 重大度判定基準

| 重大度 | 基準 |
|--------|------|
| critical | 認証バイパス・データ漏洩・セキュリティ脆弱性 |
| high | 主要機能が動作しない・データ破損の可能性 |
| medium | 機能は動くが仕様と異なる挙動 |
| low | UI の軽微なずれ・メッセージの誤り |
