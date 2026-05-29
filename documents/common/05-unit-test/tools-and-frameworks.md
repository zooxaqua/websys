# 単体テスト ツール・フレームワーク詳細（共通）

## 1. 概要

単体テスト（工程5）で使用するツール・フレームワークの詳細設定およびベストプラクティスを定義する。

---

## 2. Backend（Python）

### 2.1 Python仮想環境のセットアップ

#### 初回セットアップ（システム共通基盤）

```bash
# 仮想環境作成
cd project/backend
python3 -m venv venv

# 仮想環境アクティベート
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt
```

#### 初回セットアップ（アプリケーション）

```bash
# 仮想環境作成
cd project/apps/<app-name>/backend
python3 -m venv venv

# 仮想環境アクティベート
source venv/bin/activate  # macOS/Linux

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt
```

#### テスト実行時の仮想環境利用

> **🚨 必須**: テスト実行時は**必ず**Python仮想環境を使用すること。グローバルPythonでの実行は禁止。

**方法1: 仮想環境をアクティベートしてから実行**
```bash
# 仮想環境アクティベート
source project/backend/venv/bin/activate

# テスト実行
pytest tests/unit/logic/backend/sys/ --cov=...
```

**方法2: 仮想環境のPythonを直接指定（必須・推奨）**
```bash
# PYTHONPATH を設定して仮想環境のPythonで実行
PYTHONPATH=project/backend project/backend/venv/bin/python -m pytest tests/unit/logic/backend/sys/ --cov=...
```

**必須**: 方法2（直接指定）を使用すること。アクティベート操作が不要になり自動化しやすく、仮想環境の使用が明示的。

**禁止事項**:
- ❌ グローバルPythonでの実行（`pytest ...` のみ）
- ❌ `python -m pytest ...`（グローバルPython）
- ✅ `project/backend/venv/bin/python -m pytest ...`（仮想環境Python）

---

### 2.2 pytest — テストフレームワーク

#### インストール
```bash
pip install pytest pytest-cov
```

#### 基本設定（pytest.ini）
```ini
[pytest]
testpaths = tests/unit/logic
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --cov-report=term
    --cov-report=html
    --cov-report=json
```

#### 実行コマンド

**推奨: テストランナー（スタブ）経由で一括実行**
```bash
# システム共通基盤のテスト（テストランナー経由）
pytest tests/unit/logic/backend/sys/test_runner.py -v \
    --cov=project/backend/app/sys \
    --cov-branch \
    --cov-report=term \
    --cov-report=html:tests/unit/outputs/coverage-sys-html \
    --cov-report=json:tests/unit/outputs/coverage-sys.json \
    --junit-xml=tests/unit/outputs/test-report-sys.xml \
    > tests/unit/outputs/pytest-sys.log 2>&1
```

**代替: ディレクトリ全体を自動検出して実行**
```bash
# pytest の自動検出機能を利用（test_cases/ 配下の test_*.py を実行）
pytest tests/unit/logic/backend/sys/ \
    --cov=project/backend/app/sys \
    --cov-branch \
    --cov-report=term \
    --cov-report=html:tests/unit/outputs/coverage-sys-html \
    --cov-report=json:tests/unit/outputs/coverage-sys.json \
    --junit-xml=tests/unit/outputs/test-report-sys.xml \
    > tests/unit/outputs/pytest-sys.log 2>&1
```

**注意**: 詳細設計（工程3）が変更された場合、`test_runner.py` を再生成する。

#### フィクスチャの定義
```python
# tests/unit/logic/conftest.py
import pytest
from pathlib import Path
import json

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent.parent / "inputs" / "fixtures"

@pytest.fixture
def load_fixture(test_data_dir):
    def _load(filename: str):
        with open(test_data_dir / filename, "r") as f:
            return json.load(f)
    return _load

@pytest.fixture
def mock_dal():
    from unittest.mock import Mock
    dal = Mock()
    return dal
```

---

### 2.3 pytest-cov — カバレッジ計測

#### 分岐カバレッジの有効化
```bash
pytest --cov=<module> --cov-branch
```

#### カバレッジ目標値の設定
```bash
pytest --cov=<module> --cov-fail-under=100
```

#### 出力形式
| 形式 | オプション | 出力先 |
|------|-----------|--------|
| **Terminal** | `--cov-report=term` | 標準出力 |
| **HTML** | `--cov-report=html:path/` | HTMLレポート |
| **JSON** | `--cov-report=json:path.json` | JSONファイル |
| **XML** | `--cov-report=xml:path.xml` | XML（Cobertura形式） |

---

### 2.4 unittest.mock — モック作成

#### 基本的な使い方
```python
from unittest.mock import Mock, patch

# Mock オブジェクトの作成
mock_dal = Mock()
mock_dal.get.return_value = {"id": "test-001", "name": "Test"}
mock_dal.save.return_value = True

# 関数呼び出しの検証
mock_dal.save.assert_called_once_with({"id": "test-001", "name": "Test"})
```

#### ファイルIO のモック
```python
from unittest.mock import mock_open, patch

def test_read_file():
    mock_file = mock_open(read_data='{"key": "value"}')
    with patch("builtins.open", mock_file):
        result = read_json_file("test.json")
    
    assert result == {"key": "value"}
    mock_file.assert_called_once_with("test.json", "r")
```

#### クラスメソッドのモック
```python
@patch("module.ClassName.method_name")
def test_with_patch(mock_method):
    mock_method.return_value = "mocked_value"
    result = some_function_that_calls_method()
    assert result == "mocked_value"
```

---

### 2.5 freezegun — 時刻固定

#### インストール
```bash
pip install freezegun
```

#### 使い方
```python
from freezegun import freeze_time
from datetime import datetime

@freeze_time("2026-05-29 10:30:00")
def test_with_fixed_time():
    now = datetime.now()
    assert now.year == 2026
    assert now.month == 5
    assert now.day == 29
```

---

### 2.6 httpx — FastAPI TestClient

#### インストール
```bash
pip install httpx
```

#### 使い方
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login():
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 3. Frontend（TypeScript）

### 3.1 vitest — テストフレームワーク

#### インストール
```bash
npm install -D vitest @vitest/coverage-v8 happy-dom
```

#### 基本設定（vite.config.ts）
```typescript
import { defineConfig } from 'vite'

export default defineConfig({
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      all: true,
      lines: 100,
      branches: 100,
      functions: 100,
      statements: 100,
      include: ['src/sys/**/*.ts'],
      exclude: ['src/sys/main.ts', '**/*.test.ts', '**/*.spec.ts']
    }
  }
})
```

#### 実行コマンド

**推奨: テストランナー（スタブ）経由で一括実行**
```bash
# システム共通基盤のテスト（テストランナー経由）
vitest run tests/unit/logic/frontend/sys/test-runner.test.ts \
    --coverage \
    --reporter=junit \
    --reporter=html \
    --outputFile.junit=tests/unit/outputs/test-report-frontend-sys.xml \
    > tests/unit/outputs/vitest-frontend-sys.log 2>&1
```

**代替: ディレクトリ全体を自動検出して実行**
```bash
# vitest の自動検出機能を利用（test_cases/ 配下の *.test.ts を実行）
vitest run tests/unit/logic/frontend/sys/ \
    --coverage \
    --reporter=junit \
    --reporter=html \
    --outputFile.junit=tests/unit/outputs/test-report-frontend-sys.xml \
    > tests/unit/outputs/vitest-frontend-sys.log 2>&1
```

**注意**: 詳細設計（工程3）が変更された場合、`test-runner.test.ts` を再生成する。

---

### 3.2 @vitest/coverage-v8 — カバレッジ計測

#### カバレッジ100%の強制
```typescript
export default defineConfig({
  test: {
    coverage: {
      lines: 100,
      branches: 100,
      functions: 100,
      statements: 100,
      thresholds: {
        lines: 100,
        branches: 100,
        functions: 100,
        statements: 100
      }
    }
  }
})
```

#### カバレッジレポートの出力
```bash
vitest run --coverage
# 出力先: coverage/ ディレクトリ
```

---

### 3.3 vi.mock() — モック作成

#### APIクライアントのモック
```typescript
import { vi } from 'vitest'
import { login } from '@/sys/api/auth'

// モジュール全体をモック
vi.mock('@/sys/api/auth', () => ({
  login: vi.fn()
}))

test('login success', async () => {
  // モックの返り値を設定
  vi.mocked(login).mockResolvedValue({
    access_token: 'test-token',
    user: { id: 'u1', username: 'test' }
  })
  
  const result = await login('test', 'password')
  expect(result.access_token).toBe('test-token')
  expect(login).toHaveBeenCalledWith('test', 'password')
})
```

#### 時刻の固定
```typescript
import { vi } from 'vitest'

test('with fixed time', () => {
  const fixedDate = new Date('2026-05-29T10:30:00Z')
  vi.setSystemTime(fixedDate)
  
  const now = new Date()
  expect(now.getTime()).toBe(fixedDate.getTime())
  
  vi.useRealTimers()  // 元に戻す
})
```

---

### 3.4 happy-dom — DOM環境

#### 設定
```typescript
export default defineConfig({
  test: {
    environment: 'happy-dom'
  }
})
```

#### DOM操作のテスト
```typescript
test('DOM manipulation', () => {
  document.body.innerHTML = '<div id="app"></div>'
  const app = document.getElementById('app')
  expect(app).not.toBeNull()
  
  app!.textContent = 'Hello'
  expect(app!.textContent).toBe('Hello')
})
```

---

## 4. 共通パターン

### 4.1 パラメータ化テスト

#### Python（pytest）
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("", False),           # 空文字
    ("ab", False),         # 下限未満
    ("abc", True),         # 下限
    ("a" * 20, True),      # 上限
    ("a" * 21, False),     # 上限超過
])
def test_validate_username(input, expected):
    result = validate_username(input)
    assert result == expected
```

#### TypeScript（vitest）
```typescript
import { test, expect } from 'vitest'

test.each([
  ["", false],           // 空文字
  ["ab", false],         // 下限未満
  ["abc", true],         // 下限
  ["a".repeat(20), true],// 上限
  ["a".repeat(21), false]// 上限超過
])('validate username: %s -> %s', (input, expected) => {
  const result = validateUsername(input)
  expect(result).toBe(expected)
})
```

---

### 4.2 非同期テスト

#### Python（pytest-asyncio）
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected_value
```

#### TypeScript（vitest）
```typescript
import { test, expect } from 'vitest'

test('async function', async () => {
  const result = await asyncFunction()
  expect(result).toBe(expectedValue)
})
```

---

### 4.3 例外テスト

#### Python（pytest）
```python
import pytest

def test_raises_exception():
    with pytest.raises(ValueError, match="無効な入力"):
        invalid_function()
```

#### TypeScript（vitest）
```typescript
import { test, expect } from 'vitest'

test('throws exception', () => {
  expect(() => {
    invalidFunction()
  }).toThrow('無効な入力')
})
```

---

## 5. CI/CD 連携

### 5.1 GitHub Actions の設定例
```yaml
name: Unit Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/unit/logic/ \
            --cov=project/backend/app/sys \
            --cov-branch \
            --cov-fail-under=100 \
            --junitxml=tests/unit/outputs/test-report-sys.xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: tests/unit/outputs/coverage-sys.json
```

---

## 6. ベストプラクティス

### 6.1 テストの独立性
- 各テストは他のテストに依存しない
- テストの実行順序に依存しない
- テスト間で共有状態を持たない

### 6.2 テストの明確性
- テスト名は「何をテストしているか」が明確
- Arrange-Act-Assert パターンを使用
- 1テスト = 1アサーション（複雑な場合は複数可）

### 6.3 テストの速度
- 外部依存をモック化して高速化
- 重いテストは `@pytest.mark.slow` でマーク
- 並列実行を活用（`pytest-xdist`）

### 6.4 テストの保守性
- フィクスチャを活用して重複排除
- ヘルパー関数で共通処理を抽象化
- テストコードも実装コードと同様にリファクタリング

---

## 7. トラブルシューティング

### 7.1 カバレッジが100%にならない
**原因**:
- 未使用のコード（デッドコード）が存在
- 例外処理が網羅されていない
- 条件分岐の組み合わせが不足

**対策**:
- カバレッジレポート（HTML）で未カバー箇所を確認
- MCDC テーブルでテストケースを再設計
- デッドコードを削除

### 7.2 テストが遅い
**原因**:
- 外部依存（ファイルIO、ネットワーク）を実行している
- データベース接続が残っている

**対策**:
- モック化を徹底
- `pytest-xdist` で並列実行

### 7.3 モックが動作しない
**原因**:
- モック対象のパスが間違っている
- モックのタイミングが遅い

**対策**:
- `patch` のターゲットパスを確認（import元ではなく使用元）
- デコレーター `@patch` の順序を確認

---

## 8. 参照リンク

### 8.1 公式ドキュメント
- **pytest**: https://docs.pytest.org/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **vitest**: https://vitest.dev/
- **coverage.py**: https://coverage.readthedocs.io/

### 8.2 チュートリアル
- pytest 公式チュートリアル: https://docs.pytest.org/en/stable/getting-started.html
- vitest ガイド: https://vitest.dev/guide/

---

## 9. 参照ドキュメント

- `test-strategy.md` — テスト戦略・MCDC・境界値の詳細
- `directory-structure.md` — ディレクトリ構造・ファイル配置
- `check-program-spec.md` — チェックプログラムの仕様
