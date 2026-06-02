#!/usr/bin/env python3
"""
工程7：システム評価 - チェックプログラム

検証項目：
1. システムテストファイルの存在確認
2. テストレポートの存在確認
3. 受入基準の全項目確認（要件定義との整合性）
4. テスト実行結果ファイルの存在確認

実行方法：
    python .github/checks/common/phase-07-check.py

出力先：
    .github/checks/common/phase-07-result.json

出力形式：
    {
        "status": "pass" | "fail",
        "errors": [],
        "warnings": [],
        "timestamp": "2026-06-02T12:00:00Z",
        "phase": "07"
    }
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class Phase07Checker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_system_test_report(self) -> bool:
        """システムテストレポートの存在確認"""
        report_sys = self.project_root / "documents" / "sys" / "07-system-test-report.md"
        
        if not report_sys.exists():
            self.errors.append("システムテストレポート（sys）が存在しません: documents/sys/07-system-test-report.md")
            return False
        
        # レポートの内容確認
        content = report_sys.read_text(encoding="utf-8")
        
        # 必須セクションの確認
        required_sections = [
            "テスト実施概要",
            "テスト結果",
            "リグレッションテスト",
            "セキュリティテスト",
            "性能テスト",
            "総合判定"
        ]
        
        for section in required_sections:
            if section not in content:
                self.errors.append(f"システムテストレポートに必須セクション '{section}' が含まれていません")
        
        return len(self.errors) == 0
    
    def check_test_outputs(self) -> bool:
        """テスト結果ファイルの存在確認"""
        output_dir = self.project_root / "tests" / "system" / "outputs"
        
        if not output_dir.exists():
            self.errors.append("テスト結果ディレクトリが存在しません: tests/system/outputs/")
            return False
        
        # リグレッションテスト結果
        regression_log = output_dir / "regression-integration-test.log"
        if not regression_log.exists():
            self.warnings.append("リグレッションテスト実行ログが存在しません: regression-integration-test.log")
        
        return True
    
    def check_acceptance_criteria(self) -> bool:
        """受入基準の確認"""
        requirements_dir = self.project_root / "documents" / "sys" / "01-requirements"
        acceptance_file = requirements_dir / "acceptance-criteria.md"
        
        if not acceptance_file.exists():
            self.errors.append("受入基準ファイルが存在しません: documents/sys/01-requirements/acceptance-criteria.md")
            return False
        
        # 受入基準の内容確認
        content = acceptance_file.read_text(encoding="utf-8")
        
        # 主要な受入基準IDの存在確認
        required_ac_ids = [
            "AC-SYS-001",  # ログイン機能
            "AC-SYS-002",  # ログアウト機能
            "AC-SYS-003",  # JWT検証
            "AC-SYS-010",  # ユーザー登録
            "AC-SYS-020"   # マニフェスト読み込み
        ]
        
        for ac_id in required_ac_ids:
            if ac_id not in content:
                self.errors.append(f"受入基準 '{ac_id}' が定義されていません")
        
        return len(self.errors) == 0
    
    def check_owasp_coverage(self) -> bool:
        """OWASP Top 10カバレッジ確認"""
        report_sys = self.project_root / "documents" / "sys" / "07-system-test-report.md"
        
        if not report_sys.exists():
            # 既に check_system_test_report でエラー報告済み
            return False
        
        content = report_sys.read_text(encoding="utf-8")
        
        # OWASP Top 10 の主要項目確認
        owasp_items = ["A01", "A02", "A03", "A07"]
        
        for item in owasp_items:
            if item not in content:
                self.warnings.append(f"OWASPチェック項目 '{item}' の記載がレポートに見つかりません")
        
        return True
    
    def run_all_checks(self) -> Dict[str, Any]:
        """全チェック実行"""
        print("工程7：システム評価 - チェックプログラム実行")
        print("=" * 60)
        
        # 各チェック実行
        checks = [
            ("システムテストレポート確認", self.check_system_test_report),
            ("テスト結果ファイル確認", self.check_test_outputs),
            ("受入基準確認", self.check_acceptance_criteria),
            ("OWASPカバレッジ確認", self.check_owasp_coverage)
        ]
        
        for check_name, check_func in checks:
            print(f"\n[CHECK] {check_name}...", end=" ")
            try:
                result = check_func()
                if result:
                    print("✅ OK")
                else:
                    print("❌ NG")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.errors.append(f"{check_name}でエラー: {str(e)}")
        
        # 結果判定
        status = "pass" if len(self.errors) == 0 else "fail"
        
        result = {
            "status": status,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat() + "Z",
            "phase": "07"
        }
        
        return result
    
    def save_result(self, result: Dict[str, Any]):
        """結果をJSONファイルに保存"""
        output_file = self.project_root / ".github" / "checks" / "common" / "phase-07-result.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n結果を保存しました: {output_file}")


def main():
    checker = Phase07Checker()
    result = checker.run_all_checks()
    checker.save_result(result)
    
    # 結果表示
    print("\n" + "=" * 60)
    print("チェック結果:")
    print(f"  ステータス: {result['status'].upper()}")
    print(f"  エラー数: {len(result['errors'])}")
    print(f"  警告数: {len(result['warnings'])}")
    
    if result['errors']:
        print("\nエラー:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result['warnings']:
        print("\n警告:")
        for warning in result['warnings']:
            print(f"  - {warning}")
    
    # 終了コード
    sys.exit(0 if result['status'] == 'pass' else 1)


if __name__ == "__main__":
    main()
