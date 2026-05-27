---
description: "特定の工程をprocess-managerで開始または再開する。差し戻しや工程の個別実行に使う"
agent: "process-manager"
argument-hint: "工程番号（1〜8）と対象スコープ"
---

# 工程開始 / 再開

指定された工程を開始または再開します。

## 工程番号

${phase}（1〜8）

## 対象スコープ（任意）

${scope:全体}

## やること

1. `documents/progress.json` で現在の状態を確認する
2. 工程 ${phase} に対応するサブエージェントを呼び出す
3. 前工程の成果物を入力として渡す
4. 完了後に成果物をレビューし、承認または差し戻しを判断する

## 工程対応表

| 工程 | エージェント | 入力 | 出力先 |
|------|------------|------|--------|
| 1 | 01-requirements-agent | requests/ | documents/01-requirements/ |
| 2 | 02-basic-design-agent | documents/01-requirements/ | documents/02-basic-design/ |
| 3 | 03-detail-design-agent | documents/02-basic-design/ | documents/03-detail-design/ |
| 4 | 04-coding-agent | documents/03-detail-design/ | src/ |
| 5 | 05-unit-test-agent | src/ | tests/unit/, documents/05-unit-test-report.md |
| 6 | 06-integration-test-agent | src/ | tests/integration/, documents/06-integration-test-report.md |
| 7 | 07-system-test-agent | src/ | tests/system/, documents/07-system-test-report.md |
| 8 | 08-release-agent | documents/ | documents/08-release/ |
