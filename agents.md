# Webシステム開発 — エージェント構成

## エージェント一覧

| エージェント | 種別 | 役割 | 成果物管理フォルダ |
|------------|------|------|-----------------|
| `process-manager` | **ユーザー向け（唯一）** | 全工程統括・レビュー・差し戻し判断 | `documents/progress.json` |
| `issue-manager` | サブエージェント | 課題・バグ・リスク登録管理 | `issues/` |
| `01-requirements-agent` | サブエージェント（工程1） | 要件定義 | `documents/01-requirements/` |
| `02-basic-design-agent` | サブエージェント（工程2） | 基本設計 | `documents/02-basic-design/` |
| `03-detail-design-agent` | サブエージェント（工程3） | 詳細設計 | `documents/03-detail-design/` |
| `04-coding-agent` | サブエージェント（工程4） | コーディング | `src/` |
| `05-unit-test-agent` | サブエージェント（工程5） | 単体評価 | `tests/unit/`, `documents/05-unit-test-report.md` |
| `06-integration-test-agent` | サブエージェント（工程6） | 結合評価 | `tests/integration/`, `documents/06-integration-test-report.md` |
| `07-system-test-agent` | サブエージェント（工程7） | システム評価 | `tests/system/`, `documents/07-system-test-report.md` |
| `08-release-agent` | サブエージェント（工程8） | リリース | `documents/08-release/` |

> **原則**: 各成果物フォルダは担当エージェントのみ書き込み可。他のエージェント・ユーザーは読み取り専用。

---

## 成果物オーナーシップ

| フォルダ / ファイル | オーナー（書き込み可） | 読み取り可 |
|--------------------|----------------------|-----------|
| `requests/` | ユーザー | 全エージェント |
| `documents/progress.json` | `process-manager` | 全エージェント |
| `documents/01-requirements/` | `01-requirements-agent` | 工程2以降 + process-manager |
| `documents/02-basic-design/` | `02-basic-design-agent` | 工程3以降 + process-manager |
| `documents/03-detail-design/` | `03-detail-design-agent` | 工程4以降 + process-manager |
| `src/` | `04-coding-agent` | 工程5以降 + process-manager |
| `tests/unit/` | `05-unit-test-agent` | 工程6以降 + process-manager |
| `tests/integration/` | `06-integration-test-agent` | 工程7以降 + process-manager |
| `tests/system/` | `07-system-test-agent` | `08-release-agent` + process-manager |
| `documents/05-unit-test-report.md` | `05-unit-test-agent` | 工程6以降 + process-manager |
| `documents/06-integration-test-report.md` | `06-integration-test-agent` | 工程7以降 + process-manager |
| `documents/07-system-test-report.md` | `07-system-test-agent` | `08-release-agent` + process-manager |
| `documents/08-release/` | `08-release-agent` | process-manager |
| `issues/issues.json` | `issue-manager` | 全エージェント |

---

## 連携フロー

```mermaid
flowchart TD
    User["👤 ユーザー"]
    PM["process-manager<br/>全工程統括"]
    IM["issue-manager<br/>課題管理"]

    A01["01-requirements-agent<br/>工程1: 要件定義"]
    A02["02-basic-design-agent<br/>工程2: 基本設計"]
    A03["03-detail-design-agent<br/>工程3: 詳細設計"]
    A04["04-coding-agent<br/>工程4: コーディング"]
    A05["05-unit-test-agent<br/>工程5: 単体評価"]
    A06["06-integration-test-agent<br/>工程6: 結合評価"]
    A07["07-system-test-agent<br/>工程7: システム評価"]
    A08["08-release-agent<br/>工程8: リリース"]

    D01[("documents/01-requirements/")]
    D02[("documents/02-basic-design/")]
    D03[("documents/03-detail-design/")]
    SRC[("src/")]
    T05[("tests/unit/<br/>documents/05-unit-test-report.md")]
    T06[("tests/integration/<br/>documents/06-integration-test-report.md")]
    T07[("tests/system/<br/>documents/07-system-test-report.md")]
    D08[("documents/08-release/")]
    ISS[("issues/issues.json")]

    User -->|"指示（唯一の操作口）"| PM
    PM -->|"工程1を呼び出す"| A01
    PM -->|"工程2を呼び出す"| A02
    PM -->|"工程3を呼び出す"| A03
    PM -->|"工程4を呼び出す"| A04
    PM -->|"工程5を呼び出す"| A05
    PM -->|"工程6を呼び出す"| A06
    PM -->|"工程7を呼び出す"| A07
    PM -->|"工程8を呼び出す"| A08
    PM -->|"課題登録を依頼"| IM

    A01 -->|"書き込み"| D01
    A02 -->|"読み込み"| D01
    A02 -->|"書き込み"| D02
    A03 -->|"読み込み"| D01
    A03 -->|"読み込み"| D02
    A03 -->|"書き込み"| D03
    A04 -->|"読み込み"| D03
    A04 -->|"書き込み"| SRC
    A05 -->|"読み込み"| SRC
    A05 -->|"書き込み"| T05
    A06 -->|"読み込み"| SRC
    A06 -->|"書き込み"| T06
    A07 -->|"読み込み"| SRC
    A07 -->|"書き込み"| T07
    A08 -->|"書き込み"| D08
    IM -->|"書き込み"| ISS

    PM -->|"成果物レビュー"| D01
    PM -->|"成果物レビュー"| D02
    PM -->|"成果物レビュー"| D03
    PM -->|"成果物レビュー"| SRC
    PM -->|"成果物レビュー"| T05
    PM -->|"成果物レビュー"| T06
    PM -->|"成果物レビュー"| T07
    PM -->|"成果物レビュー"| D08

    A05 -.->|"バグ報告"| IM
    A06 -.->|"バグ報告"| IM
    A07 -.->|"バグ報告"| IM
```

---

## 差し戻しフロー

```mermaid
flowchart LR
    PM["process-manager"]

    PM -->|"テスト失敗（実装起因）"| A04["04-coding-agent"]
    PM -->|"テスト失敗（設計起因）"| A03["03-detail-design-agent"]
    PM -->|"設計不整合"| A02["02-basic-design-agent"]
    PM -->|"要件漏れ"| A01["01-requirements-agent"]
    PM -->|"セキュリティ問題"| A04
    PM -->|"セキュリティ（アーキ起因）"| A03
```

---

## ディレクトリ構成（参考）

```
websys/
├── agents.md               ← このファイル（エージェント構成）
├── requests/               ← ユーザーが置く要求仕様・議事録
├── documents/              ← 全設計書・テストレポート（エージェントが生成）
│   ├── progress.json       ← process-manager が管理
│   ├── 01-requirements/
│   ├── 02-basic-design/
│   ├── 03-detail-design/
│   ├── 05-unit-test-report.md
│   ├── 06-integration-test-report.md
│   ├── 07-system-test-report.md
│   └── 08-release/
├── src/                    ← 実装ソース（04-coding-agent が生成）
│   ├── system/
│   └── apps/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── system/
├── issues/
│   └── issues.json         ← issue-manager が管理
└── .github/
    ├── agents/             ← エージェント定義
    ├── skills/             ← スキル（専門知識）
    └── prompts/            ← プロンプトテンプレート
```
