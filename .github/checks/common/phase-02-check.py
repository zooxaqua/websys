#!/usr/bin/env python3
"""
工程2: 基本設計チェックプログラム

検証項目:
1. ファイル存在確認
2. ID重複チェック
3. 相互参照の整合性チェック
4. フォーマット確認
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set


class Phase02Checker:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.root = Path(__file__).resolve().parents[3]  # websys/
        
    def check_file_exists(self, filepath: str) -> bool:
        """ファイル存在確認"""
        full_path = self.root / filepath
        if not full_path.exists():
            self.errors.append(f"ファイルが存在しません: {filepath}")
            return False
        return True
    
    def check_sys_basic_design(self) -> bool:
        """システム共通基盤の基本設計確認"""
        print("✓ システム共通基盤の基本設計を確認中...")
        
        sys_dir = "documents/sys/02-basic-design"
        required_files = [
            "architecture.md",
            "api-design.md",
            "screen-design.md",
            "manifest-schema.md",
            "directory-structure.md"
        ]
        
        all_exist = True
        for filename in required_files:
            filepath = f"{sys_dir}/{filename}"
            if not self.check_file_exists(filepath):
                all_exist = False
        
        return all_exist
    
    def check_app_basic_design(self) -> bool:
        """アプリケーションの基本設計確認"""
        print("✓ アプリケーションの基本設計を確認中...")
        
        app_dir = "documents/app/02-basic-design"
        required_files = [
            "architecture.md",
            "api-design.md",
            "screen-design.md",
            "manifest-schema.md",
            "directory-structure.md"
        ]
        
        all_exist = True
        for filename in required_files:
            filepath = f"{app_dir}/{filename}"
            if not self.check_file_exists(filepath):
                all_exist = False
        
        return all_exist
    
    def check_api_ids(self) -> bool:
        """API IDの重複チェック"""
        print("✓ API IDの重複をチェック中...")
        
        api_ids: Set[str] = set()
        duplicates: List[str] = []
        
        # システム共通基盤API
        sys_api_file = self.root / "documents/sys/02-basic-design/api-design.md"
        if sys_api_file.exists():
            content = sys_api_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if line.startswith('### API-SYS-'):
                    api_id = line.split(':')[0].replace('### ', '').strip()
                    if api_id in api_ids:
                        duplicates.append(api_id)
                    else:
                        api_ids.add(api_id)
        
        # アプリケーションAPI
        app_api_file = self.root / "documents/app/02-basic-design/api-design.md"
        if app_api_file.exists():
            content = app_api_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if line.startswith('### API-TODO-'):
                    api_id = line.split(':')[0].replace('### ', '').strip()
                    if api_id in api_ids:
                        duplicates.append(api_id)
                    else:
                        api_ids.add(api_id)
        
        if duplicates:
            self.errors.append(f"API IDが重複しています: {', '.join(duplicates)}")
            return False
        
        print(f"  → {len(api_ids)}件のAPI IDを検出（重複なし）")
        return True
    
    def check_screen_ids(self) -> bool:
        """画面IDの重複チェック"""
        print("✓ 画面IDの重複をチェック中...")
        
        screen_ids: Set[str] = set()
        duplicates: List[str] = []
        
        # システム共通基盤画面
        sys_screen_file = self.root / "documents/sys/02-basic-design/screen-design.md"
        if sys_screen_file.exists():
            content = sys_screen_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if 'SCREEN-SYS-' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) > 1:
                        screen_id = parts[1].strip()
                        if screen_id.startswith('SCREEN-SYS-') and screen_id not in ['SCREEN-SYS-001', '']:
                            if screen_id in screen_ids:
                                duplicates.append(screen_id)
                            else:
                                screen_ids.add(screen_id)
        
        # アプリケーション画面
        app_screen_file = self.root / "documents/app/02-basic-design/screen-design.md"
        if app_screen_file.exists():
            content = app_screen_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if 'SCREEN-TODO-' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) > 1:
                        screen_id = parts[1].strip()
                        if screen_id.startswith('SCREEN-TODO-') and screen_id not in ['']:
                            if screen_id in screen_ids:
                                duplicates.append(screen_id)
                            else:
                                screen_ids.add(screen_id)
        
        if duplicates:
            self.errors.append(f"画面IDが重複しています: {', '.join(duplicates)}")
            return False
        
        print(f"  → {len(screen_ids)}件の画面IDを検出（重複なし）")
        return True
    
    def check_requirements_reference(self) -> bool:
        """工程1（要件定義）との整合性チェック"""
        print("✓ 工程1（要件定義）との整合性をチェック中...")
        
        # 工程1のFR-SYS IDを抽出
        sys_req_file = self.root / "documents/sys/01-requirements/requirements.md"
        fr_sys_ids: Set[str] = set()
        
        if sys_req_file.exists():
            content = sys_req_file.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if 'FR-SYS-' in line and '|' in line:
                    parts = line.split('|')
                    if len(parts) > 1:
                        fr_id = parts[1].strip()
                        if fr_id.startswith('FR-SYS-'):
                            fr_sys_ids.add(fr_id)
        
        # 工程2で参照されているFR-SYS IDを抽出
        sys_arch_file = self.root / "documents/sys/02-basic-design/architecture.md"
        referenced_ids: Set[str] = set()
        
        if sys_arch_file.exists():
            content = sys_arch_file.read_text(encoding='utf-8')
            for fr_id in fr_sys_ids:
                if fr_id in content:
                    referenced_ids.add(fr_id)
        
        # 警告: 一部の要件が基本設計で参照されていない可能性
        if len(referenced_ids) < len(fr_sys_ids) * 0.5:  # 50%以下の参照率
            self.warnings.append(
                f"工程1の要件（FR-SYS）の一部が基本設計で参照されていない可能性があります "
                f"（参照率: {len(referenced_ids)}/{len(fr_sys_ids)}）"
            )
        
        print(f"  → 工程1の要件: {len(fr_sys_ids)}件、工程2で参照: {len(referenced_ids)}件")
        return True
    
    def check_manifest_format(self) -> bool:
        """manifest.json フォーマットチェック"""
        print("✓ manifest.jsonのフォーマットをチェック中...")
        
        manifest_file = self.root / "documents/app/02-basic-design/manifest-schema.md"
        
        if not manifest_file.exists():
            self.errors.append("manifest-schema.md が見つかりません")
            return False
        
        content = manifest_file.read_text(encoding='utf-8')
        
        # 必須フィールドの確認
        required_fields = [
            '"name"',
            '"displayName"',
            '"version"',
            '"description"',
            '"entryPoint"',
            '"apiPrefix"'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in content:
                missing_fields.append(field)
        
        if missing_fields:
            self.errors.append(f"manifest.jsonの必須フィールドが記載されていません: {', '.join(missing_fields)}")
            return False
        
        print(f"  → manifest.jsonスキーマの必須フィールドを確認（{len(required_fields)}件）")
        return True
    
    def run(self) -> Dict[str, Any]:
        """チェック実行"""
        print("=" * 70)
        print("工程2: 基本設計チェックプログラム")
        print("=" * 70)
        print()
        
        # ファイル存在確認
        sys_ok = self.check_sys_basic_design()
        app_ok = self.check_app_basic_design()
        
        # ID重複チェック
        api_ok = self.check_api_ids()
        screen_ok = self.check_screen_ids()
        
        # 相互参照チェック
        ref_ok = self.check_requirements_reference()
        
        # フォーマット確認
        manifest_ok = self.check_manifest_format()
        
        # 結果判定
        all_passed = (
            sys_ok and app_ok and
            api_ok and screen_ok and
            ref_ok and manifest_ok and
            len(self.errors) == 0
        )
        
        status = "pass" if all_passed else "fail"
        
        result = {
            "status": status,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "phase": "02"
        }
        
        # 結果出力
        print()
        print("=" * 70)
        print("チェック結果")
        print("=" * 70)
        
        if self.errors:
            print(f"✗ エラー: {len(self.errors)}件")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✓ エラーなし")
        
        if self.warnings:
            print(f"⚠ 警告: {len(self.warnings)}件")
            for warning in self.warnings:
                print(f"  - {warning}")
        else:
            print("✓ 警告なし")
        
        print()
        print(f"ステータス: {status.upper()}")
        print("=" * 70)
        
        return result


def main():
    checker = Phase02Checker()
    result = checker.run()
    
    # 結果をJSONファイルに保存
    output_dir = Path(__file__).parent
    output_file = output_dir / "phase-02-result.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果を保存しました: {output_file}")
    
    # 終了コード
    sys.exit(0 if result['status'] == 'pass' else 1)


if __name__ == '__main__':
    main()
