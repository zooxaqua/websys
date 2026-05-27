---
description: "Webシステム開発をprocess-managerで開始する。工程1（要件定義）からプロジェクト全体を立ち上げる"
agent: "process-manager"
argument-hint: "開発対象（例：共通基盤のみ、共通基盤＋アプリA）"
---

# 開発開始

Webシステム開発プロジェクトを工程1（要件定義）から開始します。

## 対象

${target:Webシステム共通基盤}

## やること

1. `documents/progress.json` を初期化する（全工程 `not-started`）
2. 開発対象・スコープをユーザーに確認する
3. `01-requirements-agent` を呼び出して工程1（要件定義）を開始する
4. 完了後、成果物をレビューして工程2へ進むか判断する
