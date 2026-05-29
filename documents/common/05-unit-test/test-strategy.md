# 単体テスト戦略書（共通）

## 1. 概要

システム共通基盤（sys）およびアプリケーション（app）の全コンポーネントに対する単体テストの実施方針を定める。  
**MCDC 100%達成** および **境界値テストの完全実施** を必達目標とする。

---

## 2. テスト対象の選定方針

### 2.1 対象範囲
以下のレイヤーの全コンポーネントを対象とする：

#### Backend（Python）
- **API層**: エンドポイント、リクエスト/レスポンスハンドラー
- **Service層**: ビジネスロジック、ドメインルール
- **DAL層**: データアクセスロジック、CRUD操作
- **Models層**: データモデル、バリデーション、シリアライズ
- **Core層**: 認証、例外処理、ミドルウェア、設定管理

#### Frontend（TypeScript）
- **API層**: APIクライアント、HTTPリクエスト処理
- **Utils層**: ユーティリティ関数、ヘルパー、バリデーション
- **Components層**: UIコンポーネント（Alpine.jsディレクティブ）
- **Pages層**: ページロジック、ライフサイクル管理

### 2.2 対象外
- エントリーポイントファイル（`main.py`, `main.ts`, `__init__.py`）
- ビルド設定ファイル（`vite.config.ts`, `tsconfig.json`）
- テスト用フィクスチャ・スタブ・モック

### 2.3 優先度設定
| 優先度 | 対象 | 理由 |
|--------|------|------|
| **High** | 認証・セキュリティ・DAL・Service | 障害影響大、ビジネスクリティカル |
| **Medium** | API・Core・Utils | 利用頻度高、機能重要 |
| **Low** | Config・Health・Static | 障害影響小、単純処理 |

---

## 3. MCDC 100%達成方針

### 3.1 MCDC（Modified Condition/Decision Coverage）とは
各条件（condition）が独立して判定（decision）の結果を変える組み合わせを網羅するカバレッジ基準。

**定義**:
- **Condition**: 個別の真偽値（例: `user != None`, `password == stored_password`）
- **Decision**: 複数のConditionを組み合わせた判定全体（例: `user and password_match`）
- **MCDC**: 各Conditionが単独でDecisionの結果を変える組み合わせを網羅

### 3.2 達成方法

#### 基本パターン1: AND条件（2条件）
```python
# 条件: A AND B
if condition_A and condition_B:
    return True
return False
```

**MCDC テストケース**:
| TC-ID | A | B | 結果 | 独立変化条件 |
|-------|---|---|------|-------------|
| TC-001 | True | True | True | - |
| TC-002 | True | False | False | B を変化 |
| TC-003 | False | - | False | A を変化 |

#### 基本パターン2: OR条件（2条件）
```python
# 条件: A OR B
if condition_A or condition_B:
    return True
return False
```

**MCDC テストケース**:
| TC-ID | A | B | 結果 | 独立変化条件 |
|-------|---|---|------|-------------|
| TC-001 | True | - | True | A を変化 |
| TC-002 | False | True | True | B を変化 |
| TC-003 | False | False | False | - |

#### 基本パターン3: 複合条件（3条件以上）
```python
# 条件: A AND B AND C
if condition_A and condition_B and condition_C:
    return True
return False
```

**MCDC テストケース**:
| TC-ID | A | B | C | 結果 | 独立変化条件 |
|-------|---|---|---|------|-------------|
| TC-001 | True | True | True | True | - |
| TC-002 | True | True | False | False | C を変化 |
| TC-003 | True | False | - | False | B を変化 |
| TC-004 | False | - | - | False | A を変化 |

### 3.3 計測ツール
- **Python**: `pytest-cov` with `--cov-branch`
- **TypeScript**: `vitest` with `--coverage.all --coverage.lines=100 --coverage.branches=100`

### 3.4 MCDC達成の確認方法
1. カバレッジレポートで **分岐カバレッジ100%** を確認
2. 各条件分岐に対して **独立変化ケース** が存在することを確認
3. 未カバーの分岐がある場合、テストケースを追加

---

## 4. 境界値テスト方針

### 4.1 対象パラメータと境界値

| カテゴリ | 境界値 | テストケース |
|---------|-------|-------------|
| **文字列長** | 0, 1, min, max, max+1 | 空文字、最小長、最大長、超過 |
| **数値** | min-1, min, max, max+1 | 下限未満、下限、上限、上限超過 |
| **配列** | 0, 1, max | 空配列、単一要素、最大数 |
| **日時** | 過去、現在、未来 | 期限切れ、現在時刻、未来 |
| **列挙型** | 有効値、無効値 | 定義済み値、未定義値 |

### 4.2 境界値テストのパターン

#### パターン1: 文字列長のバリデーション
```
仕様: min文字以上、max文字以下
```

**テストケース**:
- 空文字（0文字） → エラー
- min-1文字 → エラー
- min文字 → 成功（下限）
- (min+max)/2文字 → 成功（中間値）
- max文字 → 成功（上限）
- max+1文字 → エラー（上限超過）

#### パターン2: 数値範囲のバリデーション
```
仕様: min <= value <= max
```

**テストケース**:
- min-1 → エラー（下限未満）
- min → 成功（下限）
- (min+max)/2 → 成功（中間値）
- max → 成功（上限）
- max+1 → エラー（上限超過）

#### パターン3: 日時の有効性チェック
```
仕様: 現在時刻より未来なら有効
```

**テストケース**:
- now() - 1秒 → 無効（過去）
- now() → 境界値（同時刻：仕様により有効/無効を決定）
- now() + 1秒 → 有効（未来）

### 4.3 境界値テストの実装戦略
1. **仕様書から境界値を抽出**: 詳細設計書のバリデーションルールを確認
2. **境界値テーブル作成**: 各パラメータの境界値を一覧化
3. **テストケース生成**: 境界値テーブルからテストケースを生成
4. **実装**: パラメータ化テスト（`@pytest.mark.parametrize`, `test.each()`）を活用

---

## 5. スタブ・モック設計方針

### 5.1 モック対象の判定基準

| レイヤー | モック対象 | モック理由 |
|---------|-----------|-----------|
| **外部依存** | ファイルIO、ネットワーク、外部API | 環境依存を排除、実行速度向上 |
| **時刻** | `datetime.now()`, `Date.now()` | テストの再現性確保 |
| **下位レイヤー** | DAL呼び出し（Service層テスト時） | 単体テストの独立性確保 |
| **認証** | セッション・トークン検証 | テストデータの簡略化 |

### 5.2 モック実装方針

#### Python（pytest）
| 対象 | モック方法 |
|------|-----------|
| **ファイルIO** | `unittest.mock.mock_open()` |
| **DAL呼び出し** | `pytest.fixture` + `unittest.mock.Mock()` |
| **時刻** | `freezegun` パッケージ |
| **外部API** | `responses` パッケージ（HTTPモック） |

#### TypeScript（vitest）
| 対象 | モック方法 |
|------|-----------|
| **ファイルIO** | `vi.mock('fs')` |
| **API呼び出し** | `vi.fn()` でモック関数作成 |
| **時刻** | `vi.setSystemTime()` |
| **外部API** | `vi.mock('api-module')` |

### 5.3 フィクスチャ配置方針
```
tests/unit/inputs/fixtures/
├── <domain>.json          ← ドメインエンティティのテストデータ
└── <scenario>.json        ← シナリオ別テストデータ
```

**命名規則**:
- ファイル名: `<domain>_<scenario>.json`（例: `users_valid.json`, `sessions_expired.json`）
- データ構造: 配列または辞書形式でJSONシリアライズ可能

### 5.4 モック実装の原則
1. **最小限のモック**: 必要な依存のみモック化（過度なモックは避ける）
2. **現実的なデータ**: 本番環境に近いテストデータを使用
3. **検証の明示**: モックの呼び出し回数・引数を検証
4. **再利用性**: フィクスチャとして共通化

---

## 6. テストツール・フレームワーク

### 6.1 Backend（Python）
| ツール | 用途 | インストール |
|--------|------|-------------|
| `pytest` | テストフレームワーク | `pip install pytest` |
| `pytest-cov` | カバレッジ計測 | `pip install pytest-cov` |
| `unittest.mock` | モック作成 | 標準ライブラリ |
| `freezegun` | 時刻固定 | `pip install freezegun` |
| `httpx` | FastAPI TestClient | `pip install httpx` |

### 6.2 Frontend（TypeScript）
| ツール | 用途 | インストール |
|--------|------|-------------|
| `vitest` | テストフレームワーク | `npm install -D vitest` |
| `@vitest/coverage-v8` | カバレッジ計測 | `npm install -D @vitest/coverage-v8` |
| `happy-dom` | DOM環境 | `npm install -D happy-dom` |

詳細は `tools-and-frameworks.md` を参照。

---

## 7. エビデンス形式

### 7.1 テスト結果レポート
| 形式 | ファイル名 | 用途 |
|------|-----------|------|
| **JUnit XML** | `test-report.xml` | CI/CD連携、自動判定 |
| **HTML** | `test-report.html` | 人間可読レポート |
| **JSON** | `test-results.json` | プログラム処理用 |

### 7.2 カバレッジレポート
| 形式 | ファイル名 | 用途 |
|------|-----------|------|
| **JSON** | `coverage.json` | カバレッジ率の自動判定 |
| **HTML** | `coverage-html/index.html` | 詳細カバレッジ閲覧 |
| **Terminal** | 標準出力 | 実行時の即時確認 |

### 7.3 出力先
- システム共通基盤: `tests/unit/outputs/`
- アプリケーション: `project/apps/<app-name>/tests/unit/outputs/`

---

## 8. 承認基準（process-manager へ返却する条件）

以下の全条件を満たすこと：

- [ ] **全テストが PASS**（FAIL が 0件）
- [ ] **MCDC カバレッジ 100%**（ライン100% かつ 分岐100%）
- [ ] **境界値テストがすべて実装・PASS**
- [ ] **重大バグ（Critical/High）が 0件**
- [ ] **テスト結果レポートが完成**（JUnit XML + HTML + レポートMarkdown）
- [ ] **チェックプログラムが PASS**（`.github/checks/common/phase-05-check.py` の実行結果が `status: "pass"`）

---

## 9. 実施手順

### ステップ1: テスト対象の洗い出し
1. 詳細設計書（`03-detail-design/class-design.md`）から全クラス・関数を列挙
2. 実装コードと設計書の対応関係を確認
3. 各モジュールのテスト優先度を決定（High → Medium → Low）

### ステップ2: テストケース設計
1. **MCDC テーブル作成**: 各条件分岐に対してMCDCテーブルを作成
2. **境界値テーブル作成**: 各パラメータの境界値を一覧化
3. **テストケース一覧化**: TC-IDを付与してスプレッドシートまたはMarkdownで管理

### ステップ3: フィクスチャ準備
1. テストデータ作成（`tests/unit/inputs/fixtures/*.json`）
2. スタブ・モック実装（`tests/unit/inputs/stubs/*.py|.ts`）

### ステップ4: テストランナー（スタブ）の作成
**目的**: 変更された関数のテストを1コマンドでまとめて実行できるようにする

#### Backend（Python）
`tests/unit/logic/backend/sys/test_runner.py` を作成：
```python
"""
単体テスト メインランナー（スタブ）
詳細設計の変更時に再生成される
"""
import pytest
from test_cases import test_auth, test_dal, test_services

# 変更されたモジュールのテストケースをまとめて実行
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

#### Frontend（TypeScript）
`tests/unit/logic/frontend/sys/test-runner.test.ts` を作成：
```typescript
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

**注意**: 詳細設計（工程3）が変更された場合、このテストランナーを再生成する。

### ステップ5: 個別テストケースの実装
1. テストフレームワークのセットアップ
2. 個別テストコード作成（`tests/unit/logic/*/test_cases/*.py|.ts`）
3. モック・フィクスチャの注入

### ステップ6: テスト実行・カバレッジ計測（1コマンド実行）
**テストランナー経由で全テストを一括実行**:

#### Backend（Python）
```bash
# システム共通基盤のテスト
pytest tests/unit/logic/backend/sys/test_runner.py -v \
  --cov=project/backend/app/sys \
  --cov-branch \
  --cov-report=term \
  --cov-report=html:tests/unit/outputs/coverage-sys-html \
  --cov-report=json:tests/unit/outputs/coverage-sys.json \
  --junit-xml=tests/unit/outputs/test-report-sys.xml \
  > tests/unit/outputs/pytest-sys.log 2>&1
```

#### Frontend（TypeScript）
```bash
# システム共通基盤のテスト
npm test -- tests/unit/logic/frontend/sys/test-runner.test.ts \
  --coverage \
  --reporter=junit \
  --outputFile=tests/unit/outputs/test-report-frontend-sys.xml \
  > tests/unit/outputs/vitest-frontend-sys.log 2>&1
```

#### アプリケーションのテスト
```bash
# Backendアプリ
pytest project/apps/<app-name>/tests/unit/logic/backend/test_runner.py -v \
  --cov=project/apps/<app-name>/backend/app \
  --cov-report=html:project/apps/<app-name>/tests/unit/outputs/coverage-html \
  --junit-xml=project/apps/<app-name>/tests/unit/outputs/test-report.xml

# Frontendアプリ
npm test -- project/apps/<app-name>/tests/unit/logic/frontend/test-runner.test.ts \
  --coverage \
  --reporter=junit
```

### ステップ7: 結果分析・追加テスト
1. カバレッジレポートで未カバー箇所を確認
2. 不足しているテストケースを追加
3. 失敗テストをデバッグ・修正（バグの場合は `issue-manager` に登録）
4. **テストランナー（スタブ）を更新**: 追加したテストケースをテストランナーに反映

### ステップ8: テスト結果レポート作成
- `documents/sys/05-unit-test-report.md`（システム共通基盤）
- `documents/app/05-unit-test-report.md`（アプリケーション）

### ステップ9: チェックプログラム実行
```bash
python .github/checks/common/phase-05-check.py
cat .github/checks/common/phase-05-result.json
```

---

## 10. 制約事項

- **DO NOT** 実装コード（`src/`, `app/`）を直接修正しない（バグを発見した場合は `issue-manager` に登録して報告）
- **DO NOT** カバレッジが 100% 未満の状態でレポートを「完了」としない
- **DO NOT** 詳細設計と実装に乖離がある場合、無断で実装を修正しない（`issue-manager` に記録し、`process-manager` の判断を仰ぐ）
- **DO NOT** エージェント定義ファイル（`.github/agents/*.agent.md`）を編集しない
- **DO NOT** スキル定義ファイル（`.github/skills/*/SKILL.md`）を編集しない
- **DO** 詳細設計（工程3）が変更された場合、テストランナー（スタブ）を再生成する
- **DO** テストランナーは1コマンドで全テストを実行できる形式にする

---

## 11. 参照ドキュメント

- `directory-structure.md` — ディレクトリ構造の詳細
- `tools-and-frameworks.md` — ツール・フレームワークの詳細設定
- `check-program-spec.md` — チェックプログラムの仕様
- `documents/sys/05-unit-test/target-files.md` — システム共通基盤の対象ファイル一覧
- `documents/app/05-unit-test/target-files.md` — アプリケーションの対象ファイル一覧
