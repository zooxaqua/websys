# 工程5 チェックプログラム仕様書（共通）

## 1. 概要

工程5（単体評価）の成果物を自動検証するチェックプログラムの仕様を定める。  
**process-manager** が自動実行し、結果を JSON 形式で出力する。

---

## 2. 基本情報

| 項目 | 内容 |
|------|------|
| **ファイル名** | `.github/checks/common/phase-05-check.py` |
| **言語** | Python 3.9+ |
| **依存** | 標準ライブラリのみ（`json`, `os`, `pathlib`, `xml.etree.ElementTree`） |
| **出力先** | `.github/checks/common/phase-05-result.json` |
| **終了コード** | 0（成功）/ 1（失敗） |
| **実行者** | `process-manager` |

---

## 3. 検証項目

### 3.1 必須ファイルの存在確認

#### システム共通基盤（sys）
- [ ] `documents/sys/05-unit-test-report.md`
- [ ] `tests/unit/outputs/test-report-sys.xml`
- [ ] `tests/unit/outputs/coverage-sys.json`
- [ ] `tests/unit/outputs/coverage-sys-html/index.html`
- [ ] `tests/unit/outputs/pytest-sys.log`（Backend）
- [ ] `tests/unit/outputs/test-report-frontend-sys.xml`（Frontend）
- [ ] `tests/unit/outputs/coverage-frontend-sys/index.html`（Frontend）
- [ ] `tests/unit/outputs/vitest-frontend-sys.log`（Frontend）

#### アプリケーション（app）
- [ ] `documents/app/05-unit-test-report.md`
- [ ] `project/apps/<app-name>/tests/unit/outputs/test-report.xml`
- [ ] `project/apps/<app-name>/tests/unit/outputs/coverage.json`
- [ ] `project/apps/<app-name>/tests/unit/outputs/coverage-html/index.html`
- [ ] `project/apps/<app-name>/tests/unit/outputs/pytest.log`（Backend）
- [ ] `project/apps/<app-name>/tests/unit/outputs/vitest.log`（Frontend）

**検証ロジック**:
```python
from pathlib import Path

def check_files_exist(file_paths: list[str]) -> list[dict]:
    errors = []
    for path in file_paths:
        if not Path(path).exists():
            errors.append({
                "code": "MISSING_FILE",
                "message": f"必須ファイルが存在しません: {path}"
            })
    return errors
```

---

### 3.2 テスト結果の確認

JUnit XML ファイルから以下を確認：
- [ ] `failures="0"`（失敗テスト数が0）
- [ ] `errors="0"`（エラー数が0）
- [ ] `tests > 0`（テストが実行されている）

**検証ロジック**:
```python
import xml.etree.ElementTree as ET

def check_junit_xml(xml_path: str) -> dict:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # testsuites または testsuite を探す
    testsuite = root if root.tag == "testsuite" else root.find("testsuite")
    
    total_tests = int(testsuite.get("tests", 0))
    failures = int(testsuite.get("failures", 0))
    errors = int(testsuite.get("errors", 0))
    
    result = {
        "total_tests": total_tests,
        "failures": failures,
        "errors": errors
    }
    
    if failures > 0 or errors > 0:
        return {
            "code": "TEST_FAILED",
            "message": f"失敗テストが存在します: {failures + errors}件",
            "details": {
                "file": xml_path,
                "failures": failures,
                "errors": errors
            }
        }
    
    if total_tests == 0:
        return {
            "code": "NO_TESTS",
            "message": "テストが実行されていません",
            "details": {"file": xml_path}
        }
    
    return None  # 成功
```

---

### 3.3 カバレッジの確認

カバレッジ JSON ファイルから以下を確認：
- [ ] `percent_covered == 100.0`（ライン100%）
- [ ] `percent_covered_branch == 100.0`（分岐100%）

**検証ロジック**:
```python
import json

def check_coverage(json_path: str, required: float = 100.0) -> dict:
    with open(json_path, "r") as f:
        data = json.load(f)
    
    # pytest-cov の形式
    line_coverage = data.get("totals", {}).get("percent_covered", 0.0)
    
    if line_coverage < required:
        return {
            "code": "COVERAGE_LOW",
            "message": f"カバレッジが不足しています: {line_coverage}% (期待値: {required}%)",
            "details": {
                "file": json_path,
                "actual": line_coverage,
                "expected": required
            }
        }
    
    return None  # 成功
```

---

### 3.4 重大バグの確認

`issues/issues.json` から以下を確認：
- [ ] `status: "open"` かつ `severity: "critical" または "high"` のバグが **0件**

**検証ロジック**:
```python
import json

def check_critical_bugs(issues_path: str = "issues/issues.json") -> dict:
    try:
        with open(issues_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        return None  # issues.json がない場合はスキップ
    
    open_critical = [
        issue for issue in data.get("issues", [])
        if issue.get("status") == "open" and issue.get("severity") in ["critical", "high"]
    ]
    
    if open_critical:
        return {
            "code": "CRITICAL_BUG",
            "message": f"未解決の重大バグが存在します: {len(open_critical)}件",
            "details": {
                "critical": sum(1 for i in open_critical if i["severity"] == "critical"),
                "high": sum(1 for i in open_critical if i["severity"] == "high"),
                "issues": [{"id": i["id"], "severity": i["severity"], "title": i["title"]} for i in open_critical]
            }
        }
    
    return None  # 成功
```

---

### 3.5 レポートの完全性確認

`documents/sys/05-unit-test-report.md` および `documents/app/05-unit-test-report.md` に以下のセクションが存在することを確認：
- [ ] "## テスト結果サマリー"
- [ ] "## カバレッジ達成状況"
- [ ] "## 失敗テスト一覧"（失敗がある場合）
- [ ] "## バグ報告"（バグがある場合）

**検証ロジック**:
```python
def check_report_sections(report_path: str, required_sections: list[str]) -> list[dict]:
    with open(report_path, "r") as f:
        content = f.read()
    
    warnings = []
    for section in required_sections:
        if section not in content:
            warnings.append({
                "code": "INCOMPLETE_REPORT",
                "message": f"レポートに「{section}」セクションがありません",
                "details": {"file": report_path}
            })
    
    return warnings
```

---

## 4. 出力形式

### 4.1 成功時（全検証項目OK）
```json
{
  "status": "pass",
  "phase": "05",
  "timestamp": "2026-05-29T10:30:00Z",
  "errors": [],
  "warnings": [],
  "summary": {
    "sys": {
      "total_tests": 350,
      "passed_tests": 350,
      "failed_tests": 0,
      "coverage_line": 100.0,
      "coverage_branch": 100.0
    },
    "app": {
      "total_tests": 88,
      "passed_tests": 88,
      "failed_tests": 0,
      "coverage_line": 100.0,
      "coverage_branch": 100.0
    },
    "critical_bugs": 0,
    "high_bugs": 0
  }
}
```

### 4.2 失敗時（検証項目NG）
```json
{
  "status": "fail",
  "phase": "05",
  "timestamp": "2026-05-29T10:30:00Z",
  "errors": [
    {
      "code": "MISSING_FILE",
      "message": "必須ファイルが存在しません: tests/unit/outputs/test-report-sys.xml"
    },
    {
      "code": "COVERAGE_LOW",
      "message": "カバレッジが不足しています: 95.5% (期待値: 100%)",
      "details": {
        "file": "tests/unit/outputs/coverage-sys.json",
        "actual": 95.5,
        "expected": 100.0
      }
    },
    {
      "code": "TEST_FAILED",
      "message": "失敗テストが存在します: 5件",
      "details": {
        "file": "tests/unit/outputs/test-report-sys.xml",
        "failures": 3,
        "errors": 2
      }
    },
    {
      "code": "CRITICAL_BUG",
      "message": "未解決の重大バグが存在します: 2件",
      "details": {
        "critical": 1,
        "high": 1,
        "issues": [
          {"id": "BUG-001", "severity": "critical", "title": "認証バイパス"},
          {"id": "BUG-005", "severity": "high", "title": "セッション漏洩"}
        ]
      }
    }
  ],
  "warnings": [
    {
      "code": "INCOMPLETE_REPORT",
      "message": "レポートに「失敗テスト一覧」セクションがありません",
      "details": {
        "file": "documents/sys/05-unit-test-report.md"
      }
    }
  ],
  "summary": {
    "sys": {
      "total_tests": 320,
      "passed_tests": 315,
      "failed_tests": 5,
      "coverage_line": 95.5,
      "coverage_branch": 93.2
    },
    "app": {
      "total_tests": 60,
      "passed_tests": 60,
      "failed_tests": 0,
      "coverage_line": 100.0,
      "coverage_branch": 100.0
    },
    "critical_bugs": 1,
    "high_bugs": 1
  }
}
```

---

## 5. エラーコード一覧

| コード | 重大度 | 説明 |
|--------|-------|------|
| `MISSING_FILE` | Error | 必須ファイルが存在しない |
| `TEST_FAILED` | Error | テストが失敗している |
| `COVERAGE_LOW` | Error | カバレッジが100%未満 |
| `CRITICAL_BUG` | Error | 未解決の重大バグが存在 |
| `NO_TESTS` | Error | テストが実行されていない |
| `INCOMPLETE_REPORT` | Warning | レポートに必須セクションがない |
| `INVALID_FORMAT` | Error | ファイル形式が不正 |

---

## 6. 実行方法

### 6.1 コマンドライン実行
```bash
python .github/checks/common/phase-05-check.py
```

### 6.2 結果確認
```bash
cat .github/checks/common/phase-05-result.json | jq .
```

### 6.3 終了コードによる判定
```bash
python .github/checks/common/phase-05-check.py
if [ $? -eq 0 ]; then
  echo "✅ チェック合格"
else
  echo "❌ チェック不合格"
fi
```

---

## 7. 実装ガイドライン

### 7.1 基本構造
```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    errors = []
    warnings = []
    summary = {}
    
    # 3.1: ファイル存在確認
    errors.extend(check_files_exist([...]))
    
    # 3.2: テスト結果確認
    error = check_junit_xml("...")
    if error:
        errors.append(error)
    
    # 3.3: カバレッジ確認
    error = check_coverage("...")
    if error:
        errors.append(error)
    
    # 3.4: 重大バグ確認
    error = check_critical_bugs()
    if error:
        errors.append(error)
    
    # 3.5: レポート完全性確認
    warnings.extend(check_report_sections("...", [...]))
    
    # 結果出力
    result = {
        "status": "pass" if not errors else "fail",
        "phase": "05",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "errors": errors,
        "warnings": warnings,
        "summary": summary
    }
    
    output_path = Path(".github/checks/common/phase-05-result.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    sys.exit(0 if result["status"] == "pass" else 1)

if __name__ == "__main__":
    main()
```

### 7.2 テスト方法
チェックプログラム自体のテストも実装すること：

```python
# tests/checks/test_phase_05_check.py
import pytest
from pathlib import Path

def test_check_files_exist_success():
    errors = check_files_exist(["README.md"])  # 存在するファイル
    assert errors == []

def test_check_files_exist_failure():
    errors = check_files_exist(["non_existent.txt"])
    assert len(errors) == 1
    assert errors[0]["code"] == "MISSING_FILE"
```

---

## 8. 拡張性

### 8.1 カスタム検証の追加
新しい検証項目を追加する場合：

```python
def check_custom_rule() -> dict:
    # カスタム検証ロジック
    if not custom_condition:
        return {
            "code": "CUSTOM_ERROR",
            "message": "カスタム検証失敗",
            "details": {...}
        }
    return None

# main() に追加
error = check_custom_rule()
if error:
    errors.append(error)
```

### 8.2 アプリケーション対応
アプリケーションごとに異なる検証を行う場合：

```python
def check_app(app_name: str):
    base_path = Path(f"project/apps/{app_name}/tests/unit/outputs")
    # アプリ固有の検証
```

---

## 9. 参照ドキュメント

- `test-strategy.md` — テスト戦略・承認基準
- `directory-structure.md` — ディレクトリ構造・ファイル配置
- `tools-and-frameworks.md` — ツール・出力形式の詳細
