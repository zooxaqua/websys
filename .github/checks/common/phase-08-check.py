#!/usr/bin/env python3
"""
工程8（リリース）チェックプログラム

目的:
    リリース成果物（リリースノート、デプロイチェックリスト、ロールバック計画）の
    存在確認と必須セクションの記載確認を行う。

実行方法:
    python .github/checks/common/phase-08-check.py

出力:
    .github/checks/common/phase-08-result.json
    - status: "pass" | "fail"
    - errors: エラーメッセージリスト
    - warnings: 警告メッセージリスト
    - timestamp: 実行日時
    - phase: "08"

終了コード:
    0: 成功
    1: 失敗
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class Phase08Checker:
    """工程8チェッククラス"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.root_dir = Path(__file__).parent.parent.parent.parent
        self.sys_release_dir = self.root_dir / "documents" / "sys" / "08-release"

    def check_file_exists(self, file_path: Path, description: str) -> bool:
        """ファイル存在確認"""
        if not file_path.exists():
            self.errors.append(f"❌ {description}が存在しません: {file_path}")
            return False
        print(f"✅ {description}が存在します: {file_path}")
        return True

    def check_file_content(self, file_path: Path, required_sections: List[str], description: str) -> bool:
        """ファイル内容確認（必須セクション）"""
        if not file_path.exists():
            return False

        try:
            content = file_path.read_text(encoding="utf-8")
            missing_sections = []

            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)

            if missing_sections:
                self.errors.append(
                    f"❌ {description}に必須セクションが欠けています: {', '.join(missing_sections)}"
                )
                return False

            print(f"✅ {description}の必須セクションが全て存在します")
            return True

        except Exception as e:
            self.errors.append(f"❌ {description}の読み込みに失敗しました: {e}")
            return False

    def check_file_size(self, file_path: Path, min_size: int, description: str) -> bool:
        """ファイルサイズ確認（最低限の内容があるか）"""
        if not file_path.exists():
            return False

        size = file_path.stat().st_size
        if size < min_size:
            self.warnings.append(
                f"⚠️ {description}のファイルサイズが小さすぎます: {size} bytes（最低 {min_size} bytes）"
            )
            return False

        print(f"✅ {description}のファイルサイズは適切です: {size} bytes")
        return True

    def check_release_notes(self) -> bool:
        """リリースノート確認"""
        print("\n=== リリースノート確認 ===")
        file_path = self.sys_release_dir / "release-notes.md"

        # ファイル存在確認
        if not self.check_file_exists(file_path, "リリースノート"):
            return False

        # 必須セクション確認（絵文字を含む可能性を考慮）
        required_sections = [
            "# リリースノート",
            "概要",
            "新機能",
            "修正されたバグ",
            "既知の問題",
            "技術スタック",
            "変更されたファイル",
            "アップグレード手順",
            "動作確認済み環境",
        ]

        if not self.check_file_content(file_path, required_sections, "リリースノート"):
            return False

        # ファイルサイズ確認（最低5KB）
        self.check_file_size(file_path, 5000, "リリースノート")

        # バージョン番号の記載確認
        content = file_path.read_text(encoding="utf-8")
        if "v1.0" not in content and "1.0.0" not in content:
            self.warnings.append("⚠️ リリースノートにバージョン番号が明記されていない可能性があります")

        # リリース日の記載確認
        if "2026" not in content:
            self.warnings.append("⚠️ リリースノートにリリース日が明記されていない可能性があります")

        return True

    def check_deployment_checklist(self) -> bool:
        """デプロイチェックリスト確認"""
        print("\n=== デプロイチェックリスト確認 ===")
        file_path = self.sys_release_dir / "deployment-checklist.md"

        # ファイル存在確認
        if not self.check_file_exists(file_path, "デプロイチェックリスト"):
            return False

        # 必須セクション確認（絵文字を含む可能性を考慮）
        required_sections = [
            "# デプロイチェックリスト",
            "デプロイ前チェック",
            "デプロイ手順",
            "デプロイ後確認",
            "ロールバック手順",
            "トラブルシューティング",
        ]

        if not self.check_file_content(file_path, required_sections, "デプロイチェックリスト"):
            return False

        # ファイルサイズ確認（最低5KB）
        self.check_file_size(file_path, 5000, "デプロイチェックリスト")

        # チェックボックスの存在確認
        content = file_path.read_text(encoding="utf-8")
        checkbox_count = content.count("- [ ]")
        if checkbox_count < 10:
            self.warnings.append(
                f"⚠️ デプロイチェックリストのチェック項目が少ない可能性があります: {checkbox_count}件"
            )
        else:
            print(f"✅ チェックボックスが十分に含まれています: {checkbox_count}件")

        # 環境準備セクションの確認
        if "Python" not in content or "Node.js" not in content:
            self.warnings.append("⚠️ 環境準備（Python/Node.js）の記載が不足している可能性があります")

        return True

    def check_rollback_plan(self) -> bool:
        """ロールバック計画確認"""
        print("\n=== ロールバック計画確認 ===")
        file_path = self.sys_release_dir / "rollback-plan.md"

        # ファイル存在確認
        if not self.check_file_exists(file_path, "ロールバック計画"):
            return False

        # 必須セクション確認（絵文字を含む可能性を考慮）
        required_sections = [
            "# ロールバック計画",
            "目的",
            "ロールバック手順",
            "ロールバック判定基準",
            "ロールバック後の対応",
        ]

        if not self.check_file_content(file_path, required_sections, "ロールバック計画"):
            return False

        # ファイルサイズ確認（最低3KB）
        self.check_file_size(file_path, 3000, "ロールバック計画")

        # バックアップ手順の記載確認
        content = file_path.read_text(encoding="utf-8")
        if "backup" not in content.lower() and "バックアップ" not in content:
            self.errors.append("❌ ロールバック計画にバックアップ手順が記載されていません")
            return False

        # Phase/Stepの記載確認
        if "Phase" not in content and "ステップ" not in content and "Step" not in content:
            self.warnings.append("⚠️ ロールバック計画に段階的な手順が明記されていない可能性があります")

        return True

    def check_directory_structure(self) -> bool:
        """ディレクトリ構成確認"""
        print("\n=== ディレクトリ構成確認 ===")

        # documents/sys/08-release/ ディレクトリの存在確認
        if not self.sys_release_dir.exists():
            self.errors.append(f"❌ リリースディレクトリが存在しません: {self.sys_release_dir}")
            return False

        print(f"✅ リリースディレクトリが存在します: {self.sys_release_dir}")
        return True

    def check_issues_status(self) -> bool:
        """課題管理ファイルの確認"""
        print("\n=== 課題管理確認 ===")
        issues_file = self.root_dir / "issues" / "issues.json"

        if not issues_file.exists():
            self.warnings.append("⚠️ issues.jsonが存在しません")
            return False

        try:
            with open(issues_file, "r", encoding="utf-8") as f:
                issues_data = json.load(f)

            issues = issues_data.get("issues", [])
            critical_open = [
                issue for issue in issues
                if issue.get("severity") == "critical" and issue.get("status") == "open"
            ]

            if critical_open:
                self.warnings.append(
                    f"⚠️ Criticalな未解決課題が存在します: {len(critical_open)}件"
                )
                for issue in critical_open:
                    self.warnings.append(f"  - {issue.get('id')}: {issue.get('title')}")
            else:
                print("✅ Criticalな未解決課題はありません")

            # Medium/Lowの未解決課題を情報として記録
            medium_open = [
                issue for issue in issues
                if issue.get("severity") == "medium" and issue.get("status") == "open"
            ]
            if medium_open:
                print(f"ℹ️ Mediumな未解決課題: {len(medium_open)}件（リリース可）")

        except Exception as e:
            self.warnings.append(f"⚠️ issues.jsonの読み込みに失敗しました: {e}")
            return False

        return True

    def run_all_checks(self) -> bool:
        """全チェック実行"""
        print("=" * 60)
        print("工程8（リリース）チェックプログラム")
        print("=" * 60)

        all_passed = True

        # ディレクトリ構成確認
        if not self.check_directory_structure():
            all_passed = False

        # リリースノート確認
        if not self.check_release_notes():
            all_passed = False

        # デプロイチェックリスト確認
        if not self.check_deployment_checklist():
            all_passed = False

        # ロールバック計画確認
        if not self.check_rollback_plan():
            all_passed = False

        # 課題管理確認
        self.check_issues_status()  # 警告のみなので結果に影響しない

        return all_passed

    def save_result(self, status: str) -> None:
        """結果をJSONファイルに保存"""
        result_dir = self.root_dir / ".github" / "checks" / "common"
        result_dir.mkdir(parents=True, exist_ok=True)
        result_file = result_dir / "phase-08-result.json"

        result = {
            "status": status,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat(),
            "phase": "08",
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n結果を保存しました: {result_file}")

    def print_summary(self, status: str) -> None:
        """サマリー表示"""
        print("\n" + "=" * 60)
        print("チェック結果サマリー")
        print("=" * 60)

        if status == "pass":
            print("✅ 全てのチェックに合格しました")
        else:
            print("❌ チェックに失敗しました")

        if self.errors:
            print(f"\n❌ エラー: {len(self.errors)}件")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print(f"\n⚠️ 警告: {len(self.warnings)}件")
            for warning in self.warnings:
                print(f"  {warning}")

        print("=" * 60)


def main() -> int:
    """メイン処理"""
    checker = Phase08Checker()

    try:
        all_passed = checker.run_all_checks()
        status = "pass" if all_passed else "fail"

        checker.save_result(status)
        checker.print_summary(status)

        return 0 if all_passed else 1

    except Exception as e:
        print(f"\n❌ チェックプログラムの実行中にエラーが発生しました: {e}")
        checker.errors.append(f"実行エラー: {e}")
        checker.save_result("fail")
        return 1


if __name__ == "__main__":
    sys.exit(main())
