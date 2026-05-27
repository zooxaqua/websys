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
| `agent-builder` | メタエージェント | エージェント・スキル・プロンプト設計生成 | `.github/agents/`, `.github/skills/` |
| `requirement-analyst` | メタエージェント（サブ） | エージェント要件分析・ヒアリング | — |
| `file-generator` | メタエージェント（サブ） | カスタマイズファイル生成・書き込み | `.github/` |

> **原則**: 各成果物フォルダは担当エージェントのみ書き込み可。他のエージェント・ユーザーは読み取り専用。

---

## 成果物オーナーシップ（参照権限）

### 原則
- **設計工程（A01〜A04）**: 直前工程の成果物のみ参照
- **テスト工程（A05〜A07）**: V字工程に準拠し、対応する設計工程の成果物を参照
  - A05（単体テスト） → 詳細設計（工程3）を検証
  - A06（結合テスト） → 基本設計（工程2）を検証
  - A07（システムテスト） → 要件定義（工程1）を検証
- **process-manager** は全成果物を参照してレビュー・差し戻し判断
- **A08（リリース）** は全成果物参照（リリースノート作成のため）

### 参照権限一覧

| エージェント | 読み取り可能 | 書き込み可能 | 備考 |
|------------|------------|------------|------|
| `01-requirements-agent` | `requests/` | `documents/01-requirements/` | 初期工程 |
| `02-basic-design-agent` | `documents/01-requirements/` | `documents/02-basic-design/` | 要件を基に設計 |
| `03-detail-design-agent` | `documents/02-basic-design/` | `documents/03-detail-design/` | 基本設計を詳細化 |
| `04-coding-agent` | `documents/03-detail-design/` | `src/` | 詳細設計を実装 |
| `05-unit-test-agent` | `src/`, `documents/03-detail-design/` | `tests/unit/`, `documents/05-unit-test-report.md` | 詳細設計通りに実装されているか検証 |
| `06-integration-test-agent` | `src/`, `documents/02-basic-design/` | `tests/integration/`, `documents/06-integration-test-report.md` | 基本設計（API・連携）通りか検証 |
| `07-system-test-agent` | `src/`, `documents/01-requirements/` | `tests/system/`, `documents/07-system-test-report.md` | 要件定義を満たしているか検証 |
| `08-release-agent` | **全成果物** | `documents/08-release/` | リリースノート作成 |
| `process-manager` | **全成果物** | `documents/progress.json` | 全体統括・レビュー |
| `issue-manager` | **全成果物**（読み取り専用） | `issues/issues.json` | 課題管理 |

> **注**: 各エージェントは自身の成果物フォルダ内のファイルを読み書き可能。他のフォルダへの書き込みは禁止。

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

    %% 設計工程（直前工程の成果物のみ参照）
    A01 -->|"書き込み"| D01
    D01 -->|"読み込み"| A02
    A02 -->|"書き込み"| D02
    D02 -->|"読み込み"| A03
    A03 -->|"書き込み"| D03
    D03 -->|"読み込み"| A04
    A04 -->|"書き込み"| SRC
    
    %% テスト工程（V字工程：対応する設計工程を検証）
    SRC -->|"読み込み（実装）"| A05
    D03 -.->|"参照（詳細設計）"| A05
    A05 -->|"書き込み"| T05
    
    SRC -->|"読み込み（実装）"| A06
    D02 -.->|"参照（基本設計）"| A06
    A06 -->|"書き込み"| T06
    
    SRC -->|"読み込み（実装）"| A07
    D01 -.->|"参照（要件定義）"| A07
    A07 -->|"書き込み"| T07
    
    %% A08は例外的に全成果物参照可
    D01 & D02 & D03 & SRC & T05 & T06 & T07 -->|"読み込み（全成果物）"| A08
    A08 -->|"書き込み"| D08
    
    IM -->|"書き込み"| ISS

    %% PMは全成果物をレビュー
    D01 & D02 & D03 & SRC & T05 & T06 & T07 & D08 -->|"レビュー"| PM

    %% 課題報告
    A05 & A06 & A07 -.->|"バグ報告"| IM
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
