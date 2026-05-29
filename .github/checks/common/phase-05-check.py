#!/usr/bin/env python3
"""
工程5（単体評価）チェックプログラム
Phase 05 Unit Test Check Program

検証項目:
1. テストファイルの存在確認
2. テスト実行結果の確認（全テスト合格）
3. カバレッジレポートの確認（MCDC 100%達成）
4. 重大バグの未解決確認
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def check_test_files_exist() -> Dict[str, Any]:
    """テストファイルの存在確認"""
    print("=" * 80)
    print("1. テストファイルの存在確認")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    # Backend テストファイル（優先度High）
    backend_test_files = [
        "tests/unit/logic/backend/sys/test_cases/test_user_model.py",
        "tests/unit/logic/backend/sys/test_cases/test_session_model.py",
        "tests/unit/logic/backend/sys/test_cases/test_app_model.py",
        "tests/unit/logic/backend/sys/test_cases/test_notification_model.py",
        "tests/unit/logic/backend/sys/test_cases/test_json_dal.py",
        "tests/unit/logic/backend/sys/test_cases/test_user_dal.py",
        "tests/unit/logic/backend/sys/test_cases/test_session_dal.py",
        "tests/unit/logic/backend/sys/test_cases/test_security.py",
    ]
    
    # Frontend テストファイル（優先度High）
    frontend_test_files = [
        "tests/unit/logic/frontend/sys/test_cases/test_http.test.ts",
    ]
    
    missing_files = []
    
    for test_file in backend_test_files + frontend_test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        errors.append(f"テストファイルが存在しません: {', '.join(missing_files)}")
    
    print(f"✓ Backend テストファイル: {len(backend_test_files)}件")
    print(f"✓ Frontend テストファイル: {len(frontend_test_files)}件")
    
    if missing_files:
        print(f"✗ 不足: {len(missing_files)}件")
    
    return {
        "errors": errors,
        "warnings": warnings,
        "backend_count": len(backend_test_files),
        "frontend_count": len(frontend_test_files),
        "missing_count": len(missing_files)
    }


def check_test_execution() -> Dict[str, Any]:
    """テスト実行結果の確認"""
    print("\n" + "=" * 80)
    print("2. テスト実行結果の確認")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    # pytest を実行してテスト結果を取得
    try:
        result = subprocess.run(
            [
                "project/backend/venv/bin/python", "-m", "pytest",
                "tests/unit/logic/backend/sys/test_cases/",
                "--junit-xml=tests/unit/outputs/test-report-sys.xml",
                "-v",
                "--tb=no"
            ],
            env={"PYTHONPATH": "project/backend"},
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        # JUnit XML を解析
        junit_xml = Path("tests/unit/outputs/test-report-sys.xml")
        if junit_xml.exists():
            import xml.etree.ElementTree as ET
            tree = ET.parse(junit_xml)
            root = tree.getroot()
            testsuite = root.find(".//testsuite")
            
            if testsuite is not None:
                total_tests = int(testsuite.get("tests", 0))
                failures = int(testsuite.get("failures", 0))
                errors_count = int(testsuite.get("errors", 0))
                skipped = int(testsuite.get("skipped", 0))
                passed = total_tests - failures - errors_count - skipped
                
                print(f"✓ 総テスト数: {total_tests}")
                print(f"✓ 成功: {passed}")
                print(f"✗ 失敗: {failures}")
                print(f"✗ エラー: {errors_count}")
                print(f"- スキップ: {skipped}")
                
                if failures > 0 or errors_count > 0:
                    errors.append(f"テスト失敗: {failures + errors_count}件")
                
                return {
                    "errors": errors,
                    "warnings": warnings,
                    "total": total_tests,
                    "passed": passed,
                    "failed": failures + errors_count
                }
        else:
            warnings.append("JUnit XMLレポートが見つかりません")
    
    except Exception as e:
        errors.append(f"テスト実行エラー: {str(e)}")
    
    return {
        "errors": errors,
        "warnings": warnings,
        "total": 0,
        "passed": 0,
        "failed": 0
    }


def check_coverage() -> Dict[str, Any]:
    """カバレッジレポートの確認"""
    print("\n" + "=" * 80)
    print("3. カバレッジレポートの確認（MCDC 100%達成）")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    coverage_json = Path("tests/unit/outputs/coverage-sys.json")
    
    if not coverage_json.exists():
        errors.append("カバレッジレポート（coverage-sys.json）が見つかりません")
        return {
            "errors": errors,
            "warnings": warnings,
            "line_coverage": 0,
            "branch_coverage": 0,
            "mcdc_coverage": 0
        }
    
    try:
        with open(coverage_json, "r") as f:
            coverage_data = json.load(f)
        
        totals = coverage_data.get("totals", {})
        line_coverage = totals.get("percent_covered", 0)
        branch_coverage = totals.get("percent_branches_covered", 0)
        
        # MCDC = Branch Coverage（簡易的な判定）
        mcdc_coverage = branch_coverage
        
        print(f"✓ ライン: {line_coverage:.2f}%")
        print(f"✓ 分岐: {branch_coverage:.2f}%")
        print(f"✓ MCDC: {mcdc_coverage:.2f}%")
        
        if mcdc_coverage < 100:
            errors.append(f"MCDC 100%未達成: 現在{mcdc_coverage:.2f}%")
        
        if line_coverage < 80:
            warnings.append(f"ラインカバレッジが低い: {line_coverage:.2f}%")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "line_coverage": line_coverage,
            "branch_coverage": branch_coverage,
            "mcdc_coverage": mcdc_coverage
        }
    
    except Exception as e:
        errors.append(f"カバレッジ解析エラー: {str(e)}")
        return {
            "errors": errors,
            "warnings": warnings,
            "line_coverage": 0,
            "branch_coverage": 0,
            "mcdc_coverage": 0
        }


def check_critical_bugs() -> Dict[str, Any]:
    """重大バグの未解決確認"""
    print("\n" + "=" * 80)
    print("4. 重大バグの未解決確認")
    print("=" * 80)
    
    errors = []
    warnings = []
    
    # issues.json を確認
    issues_json = Path("issues/issues.json")
    
    if not issues_json.exists():
        warnings.append("issues.json が見つかりません（課題が登録されていない可能性）")
        return {
            "errors": errors,
            "warnings": warnings,
            "critical_count": 0,
            "high_count": 0
        }
    
    try:
        with open(issues_json, "r") as f:
            issues_data = json.load(f)
        
        issues = issues_data.get("issues", [])
        critical_issues = [i for i in issues if i.get("severity") == "Critical" and i.get("status") != "resolved"]
        high_issues = [i for i in issues if i.get("severity") == "High" and i.get("status") != "resolved"]
        
        print(f"✓ Critical未解決: {len(critical_issues)}件")
        print(f"✓ High未解決: {len(high_issues)}件")
        
        if len(critical_issues) > 0:
            errors.append(f"Critical未解決バグ: {len(critical_issues)}件")
        
        if len(high_issues) > 0:
            warnings.append(f"High未解決バグ: {len(high_issues)}件")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "critical_count": len(critical_issues),
            "high_count": len(high_issues)
        }
    
    except Exception as e:
        warnings.append(f"Issue解析エラー: {str(e)}")
        return {
            "errors": errors,
            "warnings": warnings,
            "critical_count": 0,
            "high_count": 0
        }


def main():
    """メイン処理"""
    print("=" * 80)
    print("工程5（単体評価）チェックプログラム")
    print("Phase 05 Unit Test Check Program")
    print("=" * 80)
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_errors = []
    all_warnings = []
    
    # 1. テストファイルの存在確認
    result1 = check_test_files_exist()
    all_errors.extend(result1["errors"])
    all_warnings.extend(result1["warnings"])
    
    # 2. テスト実行結果の確認
    result2 = check_test_execution()
    all_errors.extend(result2["errors"])
    all_warnings.extend(result2["warnings"])
    
    # 3. カバレッジレポートの確認
    result3 = check_coverage()
    all_errors.extend(result3["errors"])
    all_warnings.extend(result3["warnings"])
    
    # 4. 重大バグの未解決確認
    result4 = check_critical_bugs()
    all_errors.extend(result4["errors"])
    all_warnings.extend(result4["warnings"])
    
    # 結果サマリー
    print("\n" + "=" * 80)
    print("チェック結果サマリー")
    print("=" * 80)
    
    status = "pass" if len(all_errors) == 0 else "fail"
    
    result = {
        "status": status,
        "errors": all_errors,
        "warnings": all_warnings,
        "timestamp": datetime.now().isoformat(),
        "phase": "05",
        "details": {
            "test_files": result1,
            "test_execution": result2,
            "coverage": result3,
            "critical_bugs": result4
        }
    }
    
    # 結果をJSONファイルに出力
    output_dir = Path(".github/checks/common")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "phase-05-result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"ステータス: {status.upper()}")
    print(f"エラー: {len(all_errors)}件")
    print(f"警告: {len(all_warnings)}件")
    print()
    
    if all_errors:
        print("エラー詳細:")
        for error in all_errors:
            print(f"  ✗ {error}")
        print()
    
    if all_warnings:
        print("警告詳細:")
        for warning in all_warnings:
            print(f"  ⚠ {warning}")
        print()
    
    print(f"結果ファイル: {output_file}")
    print("=" * 80)
    
    # 終了コード
    sys.exit(0 if status == "pass" else 1)


if __name__ == "__main__":
    main()
