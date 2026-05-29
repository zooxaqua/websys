# 単体テスト ディレクトリ構造定義（共通）

## 1. 概要

単体テスト（工程5）における統一的なディレクトリ構造を定義する。  
**inputs/**, **logic/**, **outputs/** の3層構造で整理し、エビデンスの追跡可能性を確保する。

---

## 2. 設計原則

### 2.1 3層構造
| 層 | 役割 | 内容 |
|---|------|------|
| **inputs/** | テストデータ | フィクスチャ、スタブ、モック、期待値 |
| **logic/** | テストコード | 実際のテストロジック（*.py, *.test.ts） |
| **outputs/** | テスト結果 | JUnit XML、カバレッジ、ログ |

### 2.2 分離の利点
- **再利用性**: フィクスチャを複数テストで共有
- **保守性**: テストデータとロジックを独立管理
- **追跡性**: エビデンスを一元管理

---

## 3. 全体構造（抽象化）

### 3.1 システム共通基盤（sys）
```
tests/unit/                          ← システム共通基盤のテスト
├── inputs/                          ← テストデータ・モック（再利用可能）
│   ├── fixtures/                    ← テスト用固定データ（JSON）
│   │   ├── <entity>.json            ← エンティティ別テストデータ
│   │   └── <scenario>.json          ← シナリオ別テストデータ
│   ├── stubs/                       ← スタブ・モック実装
│   │   ├── mock_<layer>.py          ← レイヤー別モック
│   │   ├── mock_external_api.py     ← 外部APIのモック
│   │   └── mock_time.py             ← 時刻固定用ヘルパー
│   └── expected/                    ← 期待値データ
│       ├── <feature>_responses.json ← 期待レスポンス
│       ├── validation_errors.json   ← バリデーションエラーの期待値
│       └── coverage_targets.json    ← カバレッジ目標値
│
├── logic/                           ← テストコード本体
│   ├── backend/
│   │   └── sys/
│   │       ├── test_runner.py                  ← **テストランナー（スタブ）** — 全テストを一括実行
│   │       ├── conftest.py                     ← pytest設定・共通フィクスチャ
│   │       └── test_cases/                     ← 個別のテストケース
│   │           ├── test_models.py              ← モデル層のテスト
│   │           ├── test_services.py            ← サービス層のテスト
│   │           ├── test_dal.py                 ← データアクセス層のテスト
│   │           ├── test_api.py                 ← API層のテスト
│   │           └── test_core.py                ← コア層のテスト
│   └── frontend/
│       └── sys/
│           ├── test-runner.test.ts             ← **テストランナー（スタブ）** — 全テストを一括実行
│           └── test_cases/                     ← 個別のテストケース
│               ├── test-auth-api.test.ts       ← APIクライアントのテスト
│               ├── test-validation.test.ts     ← ユーティリティのテスト
│               ├── test-components.test.ts     ← コンポーネントのテスト
│               └── test-pages.test.ts          ← ページのテスト
│
└── outputs/                         ← テスト実行結果（エビデンス）
    ├── test-report-sys.xml          ← システムのJUnit形式テスト結果
    ├── coverage-sys.json            ← システムのカバレッジ（JSON）
    ├── coverage-sys-html/           ← システムのカバレッジ（HTML）
    │   ├── index.html
    │   └── <module>/
    ├── pytest-sys.log               ← システムのテスト実行ログ
    ├── test-report-frontend-sys.xml ← フロントのJUnit形式テスト結果
    ├── coverage-frontend-sys/       ← フロントのカバレッジ（HTML）
    └── vitest-frontend-sys.log      ← フロントのテスト実行ログ
```

### 3.2 アプリケーション（app）
```
project/apps/<app-name>/tests/unit/  ← アプリケーション専用のテスト
├── inputs/                          ← アプリのテストデータ
│   ├── fixtures/
│   │   └── <entity>.json            ← アプリエンティティのテストデータ
│   ├── stubs/
│   │   └── mock_<dependency>.py     ← アプリ依存のモック
│   └── expected/
│       └── <feature>_responses.json ← 期待レスポンス
│
├── logic/                           ← アプリのテストコード
│   ├── backend/
│   │   ├── test_runner.py                      ← **テストランナー（スタブ）**
│   │   ├── conftest.py                         ← pytest設定
│   │   └── test_cases/                         ← 個別のテストケース
│   │       ├── test_models.py
│   │       ├── test_services.py
│   │       ├── test_dal.py
│   │       └── test_api.py
│   └── frontend/
│       ├── test-runner.test.ts                 ← **テストランナー（スタブ）**
│       └── test_cases/                         ← 個別のテストケース
│           └── test-<module>.test.ts
│
└── outputs/                         ← アプリのテスト結果
    ├── test-report.xml              ← JUnit形式テスト結果
    ├── coverage.json                ← カバレッジ（JSON）
    ├── coverage-html/               ← カバレッジ（HTML）
    │   └── index.html
    ├── pytest.log                   ← テスト実行ログ（Backend）
    └── vitest.log                   ← テスト実行ログ（Frontend）
```

---

## 4. 命名規則

### 4.1 テストコードファイル
| 対象 | 命名規則 | 例 |
|------|---------|-----|
| **Python** | `test_<module>.py` | `test_user_dal.py`, `test_auth_service.py` |
| **TypeScript** | `test_<module>.test.ts` | `test_auth.test.ts`, `test_validation.test.ts` |

### 4.2 フィクスチャファイル
| 種類 | 命名規則 | 例 |
|------|---------|-----|
| **エンティティ別** | `<entity>.json` | `users.json`, `sessions.json` |
| **シナリオ別** | `<entity>_<scenario>.json` | `users_valid.json`, `sessions_expired.json` |

### 4.3 モック実装ファイル
| 種類 | 命名規則 | 例 |
|------|---------|-----|
| **Python** | `mock_<target>.py` | `mock_dal.py`, `mock_external_api.py` |
| **TypeScript** | `mock_<target>.ts` | `mock_api.ts`, `mock_fetch.ts` |

### 4.4 出力ファイル
| 種類 | 命名規則 | 例 |
|------|---------|-----|
| **JUnit XML** | `test-report[-<scope>].xml` | `test-report-sys.xml`, `test-report.xml` |
| **Coverage JSON** | `coverage[-<scope>].json` | `coverage-sys.json`, `coverage.json` |
| **Coverage HTML** | `coverage[-<scope>]-html/` | `coverage-sys-html/`, `coverage-html/` |
| **Log** | `pytest[-<scope>].log`, `vitest[-<scope>].log` | `pytest-sys.log`, `vitest.log` |

---

## 5. inputs/ の詳細設計

### 5.1 fixtures/ — テスト用固定データ
**用途**: テストで使用する静的データ（JSONファイル）

**配置例**:
```
inputs/fixtures/
├── <entity>_valid.json       ← 正常系データ
├── <entity>_invalid.json     ← 異常系データ
└── <entity>_boundary.json    ← 境界値データ
```

**データ構造**:
```json
[
  {
    "id": "test-001",
    "field": "value",
    "...": "..."
  }
]
```

### 5.2 stubs/ — スタブ・モック実装
**用途**: 外部依存をモック化するコード

**配置例**:
```
inputs/stubs/
├── mock_dal.py              ← DAL層のモック
├── mock_external_api.py     ← 外部APIのモック
└── mock_time.py             ← 時刻固定用ヘルパー
```

**実装例**（Python）:
```python
# mock_dal.py
from unittest.mock import Mock

def create_mock_dal():
    dal = Mock()
    dal.get.return_value = {"id": "test-001", "name": "Test"}
    dal.save.return_value = True
    return dal
```

### 5.3 expected/ — 期待値データ
**用途**: テストの期待結果を定義

**配置例**:
```
inputs/expected/
├── <feature>_responses.json    ← API期待レスポンス
├── validation_errors.json      ← バリデーションエラーの期待値
└── coverage_targets.json       ← カバレッジ目標値
```

---

## 6. logic/ の詳細設計

### 6.1 ディレクトリ構造
実装コードの構造を反映したディレクトリ構成とする。

**原則**:
- **1実装ファイル = 1テストファイル**
- **レイヤー構造を維持**（api/, services/, dal/, models/, core/）

**例**:
```
実装: project/backend/app/sys/services/auth_service.py
テスト: tests/unit/logic/backend/sys/services/test_auth_service.py
```

### 6.2 テストクラス・関数の命名
| 対象 | 命名規則 | 例 |
|------|---------|-----|
| **テストクラス** | `Test<ClassName>` | `TestAuthService`, `TestUserDAL` |
| **テスト関数** | `test_<method>_<scenario>` | `test_authenticate_success`, `test_authenticate_invalid_password` |

### 6.3 テストランナー（スタブ）の詳細

**目的**: 変更された関数のテストを1コマンドでまとめて実行できるようにする

**配置場所**:
- Backend: `tests/unit/logic/backend/sys/test_runner.py`
- Frontend: `tests/unit/logic/frontend/sys/test-runner.test.ts`

**重要な原則**:
- 詳細設計（工程3）が変更された場合、テストランナーを再生成する
- 個別のテストケースは `test_cases/` サブディレクトリに配置
- テストランナーは test_cases/ 内のテストを呼び出す

**Backend（Python）の例**:
```python
# tests/unit/logic/backend/sys/test_runner.py
"""
単体テスト メインランナー（スタブ）
詳細設計の変更時に再生成される
"""
import pytest
from test_cases import test_auth, test_dal, test_services

def test_all_changed_modules():
    """変更されたモジュールのテストをまとめて実行"""
    # 認証サービスのテスト
    test_auth.test_login_success()
    test_auth.test_login_failure()
    test_auth.test_token_validation()
    
    # DAL層のテスト
    test_dal.test_get_user()
    test_dal.test_save_user()
    
    # サービス層のテスト
    test_services.test_user_registration()
```

**Frontend（TypeScript）の例**:
```typescript
// tests/unit/logic/frontend/sys/test-runner.test.ts
/**
 * 単体テスト メインランナー（スタブ）
 * 詳細設計の変更時に再生成される
 */
import { describe, it } from 'vitest';
import { testAuthAPI } from './test_cases/test-auth-api';
import { testFetch } from './test_cases/test-fetch';

describe('変更されたモジュールのテスト', () => {
  it('認証APIのテスト', () => {
    testAuthAPI();
  });
  
  it('Fetchユーティリティのテスト', () => {
    testFetch();
  });
});
```

**実行方法**:
```bash
# Backend
pytest tests/unit/logic/backend/sys/test_runner.py -v --cov=project/backend/app/sys

# Frontend
vitest run tests/unit/logic/frontend/sys/test-runner.test.ts --coverage
```

---

## 7. outputs/ の詳細設計

### 7.1 出力ファイル一覧
| ファイル | 形式 | 用途 |
|---------|------|------|
| `test-report-*.xml` | JUnit XML | CI/CD連携、自動判定 |
| `coverage-*.json` | JSON | カバレッジ率の自動判定 |
| `coverage-*-html/` | HTML | 詳細カバレッジ閲覧 |
| `pytest-*.log` | Text | テスト実行ログ（Backend） |
| `vitest-*.log` | Text | テスト実行ログ（Frontend） |

### 7.2 JUnit XML の構造
```xml
<testsuites>
  <testsuite name="backend.sys.services" tests="15" failures="0" errors="0" time="2.345">
    <testcase classname="test_auth_service.TestAuthService" name="test_authenticate_success" time="0.123"/>
    <testcase classname="test_auth_service.TestAuthService" name="test_authenticate_invalid_password" time="0.089"/>
  </testsuite>
</testsuites>
```

### 7.3 Coverage JSON の構造
```json
{
  "meta": {
    "version": "7.2.0"
  },
  "totals": {
    "percent_covered": 100.0,
    "percent_covered_display": "100",
    "num_statements": 500,
    "missing_lines": 0
  },
  "files": {
    "project/backend/app/sys/services/auth_service.py": {
      "summary": {
        "percent_covered": 100.0,
        "num_statements": 50,
        "missing_lines": 0
      }
    }
  }
}
```

---

## 8. ディレクトリ作成コマンド

### 8.1 システム共通基盤
```bash
mkdir -p tests/unit/{inputs/{fixtures,stubs,expected},logic/backend/sys/{models,services,dal,api,core},logic/frontend/sys/{api,utils,components,pages},outputs}
```

### 8.2 アプリケーション
```bash
mkdir -p project/apps/<app-name>/tests/unit/{inputs/{fixtures,stubs,expected},logic/{backend/{models,services,dal,api},frontend},outputs}
```

---

## 9. .gitignore 設定

テスト結果（outputs/）は Git 管理対象外とする：

```gitignore
# テスト結果（エビデンス）
tests/unit/outputs/
project/apps/*/tests/unit/outputs/

# カバレッジファイル
.coverage
coverage.xml
htmlcov/
```

---

## 10. 参照ドキュメント

- `test-strategy.md` — テスト戦略・MCDC・境界値の詳細
- `tools-and-frameworks.md` — ツール・フレームワークの詳細設定
- `check-program-spec.md` — チェックプログラムの仕様
