#!/usr/bin/env python3
"""
工程1（要件定義）成果物の自動検証プログラム
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple

# プロジェクトルートディレクトリ（.github/checks/common/ から4階層上）
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOCUMENTS_ROOT = PROJECT_ROOT / "documents"

# 必須ファイルリスト
REQUIRED_FILES = [
    DOCUMENTS_ROOT / "sys" / "01-requirements" / "requirements.md",
    DOCUMENTS_ROOT / "sys" / "01-requirements" / "use-cases.md",
    DOCUMENTS_ROOT / "sys" / "01-requirements" / "acceptance-criteria.md",
    DOCUMENTS_ROOT / "app" / "01-requirements" / "requirements.md",
    DOCUMENTS_ROOT / "app" / "01-requirements" / "use-cases.md",
    DOCUMENTS_ROOT / "app" / "01-requirements" / "acceptance-criteria.md",
]

# ID パターン
REQUIREMENT_ID_PATTERN = re.compile(r"\b(?:FR|NFR|OPR)-[A-Z]+-\d{3}\b")
USECASE_ID_PATTERN = re.compile(r"\bUC-[A-Z]+-\d{3}\b")
ACCEPTANCE_ID_PATTERN = re.compile(r"\bAC-[A-Z]+-\d{3}\b")


def check_file_existence() -> Tuple[List[str], List[Path]]:
    """
    必須ファイルの存在確認
    
    Returns:
        (errors, existing_files): エラーリストと存在するファイルリスト
    """
    errors = []
    existing_files = []
    
    for file_path in REQUIRED_FILES:
        if not file_path.exists():
            errors.append(f"必須ファイルが存在しません: {file_path.relative_to(PROJECT_ROOT)}")
        else:
            existing_files.append(file_path)
    
    return errors, existing_files


def extract_ids_from_file(file_path: Path, pattern: re.Pattern) -> Set[str]:
    """
    ファイルから指定パターンのIDを抽出
    
    Args:
        file_path: 対象ファイルパス
        pattern: ID抽出パターン
    
    Returns:
        抽出されたIDのセット
    """
    ids = set()
    
    try:
        content = file_path.read_text(encoding="utf-8")
        matches = pattern.findall(content)
        ids.update(matches)
    except Exception as e:
        # エラーは上位で処理する
        pass
    
    return ids


def check_id_duplicates() -> List[str]:
    """
    要件ID・ユースケースID・受入基準IDの重複チェック
    
    Returns:
        エラーリスト
    """
    errors = []
    
    # 要件IDチェック
    req_files = [
        DOCUMENTS_ROOT / "sys" / "01-requirements" / "requirements.md",
        DOCUMENTS_ROOT / "app" / "01-requirements" / "requirements.md",
    ]
    
    all_req_ids: Dict[str, str] = {}
    for file_path in req_files:
        if not file_path.exists():
            continue
        
        ids = extract_ids_from_file(file_path, REQUIREMENT_ID_PATTERN)
        for req_id in ids:
            if req_id in all_req_ids:
                errors.append(
                    f"要件ID重複: {req_id} が {all_req_ids[req_id]} と "
                    f"{file_path.relative_to(PROJECT_ROOT)} に存在します"
                )
            else:
                all_req_ids[req_id] = str(file_path.relative_to(PROJECT_ROOT))
    
    # ユースケースIDチェック
    uc_files = [
        DOCUMENTS_ROOT / "sys" / "01-requirements" / "use-cases.md",
        DOCUMENTS_ROOT / "app" / "01-requirements" / "use-cases.md",
    ]
    
    all_uc_ids: Dict[str, str] = {}
    for file_path in uc_files:
        if not file_path.exists():
            continue
        
        ids = extract_ids_from_file(file_path, USECASE_ID_PATTERN)
        for uc_id in ids:
            if uc_id in all_uc_ids:
                errors.append(
                    f"ユースケースID重複: {uc_id} が {all_uc_ids[uc_id]} と "
                    f"{file_path.relative_to(PROJECT_ROOT)} に存在します"
                )
            else:
                all_uc_ids[uc_id] = str(file_path.relative_to(PROJECT_ROOT))
    
    # 受入基準IDチェック
    ac_files = [
        DOCUMENTS_ROOT / "sys" / "01-requirements" / "acceptance-criteria.md",
        DOCUMENTS_ROOT / "app" / "01-requirements" / "acceptance-criteria.md",
    ]
    
    all_ac_ids: Dict[str, str] = {}
    for file_path in ac_files:
        if not file_path.exists():
            continue
        
        ids = extract_ids_from_file(file_path, ACCEPTANCE_ID_PATTERN)
        for ac_id in ids:
            if ac_id in all_ac_ids:
                errors.append(
                    f"受入基準ID重複: {ac_id} が {all_ac_ids[ac_id]} と "
                    f"{file_path.relative_to(PROJECT_ROOT)} に存在します"
                )
            else:
                all_ac_ids[ac_id] = str(file_path.relative_to(PROJECT_ROOT))
    
    return errors


def check_cross_references() -> List[str]:
    """
    相互参照の整合性チェック
    
    Returns:
        エラーリスト（警告）
    """
    warnings = []
    
    # 要件ID収集
    req_files = [
        DOCUMENTS_ROOT / "sys" / "01-requirements" / "requirements.md",
        DOCUMENTS_ROOT / "app" / "01-requirements" / "requirements.md",
    ]
    all_req_ids = set()
    for file_path in req_files:
        if file_path.exists():
            all_req_ids.update(extract_ids_from_file(file_path, REQUIREMENT_ID_PATTERN))
    
    # ユースケースID収集
    uc_files = [
        DOCUMENTS_ROOT / "sys" / "01-requirements" / "use-cases.md",
        DOCUMENTS_ROOT / "app" / "01-requirements" / "use-cases.md",
    ]
    all_uc_ids = set()
    for file_path in uc_files:
        if file_path.exists():
            all_uc_ids.update(extract_ids_from_file(file_path, USECASE_ID_PATTERN))
    
    # ユースケース内で参照されている要件IDチェック
    for file_path in uc_files:
        if not file_path.exists():
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8")
            referenced_req_ids = REQUIREMENT_ID_PATTERN.findall(content)
            
            for req_id in set(referenced_req_ids):
                if req_id not in all_req_ids:
                    warnings.append(
                        f"警告: {file_path.relative_to(PROJECT_ROOT)} で参照されている "
                        f"要件ID {req_id} が要件定義書に存在しません"
                    )
        except Exception:
            pass
    
    # 受入基準内で参照されている要件ID・ユースケースIDチェック
    ac_files = [
        DOCUMENTS_ROOT / "sys" / "01-requirements" / "acceptance-criteria.md",
        DOCUMENTS_ROOT / "app" / "01-requirements" / "acceptance-criteria.md",
    ]
    
    for file_path in ac_files:
        if not file_path.exists():
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # 要件ID参照チェック
            referenced_req_ids = REQUIREMENT_ID_PATTERN.findall(content)
            for req_id in set(referenced_req_ids):
                if req_id not in all_req_ids:
                    warnings.append(
                        f"警告: {file_path.relative_to(PROJECT_ROOT)} で参照されている "
                        f"要件ID {req_id} が要件定義書に存在しません"
                    )
            
            # ユースケースID参照チェック
            referenced_uc_ids = USECASE_ID_PATTERN.findall(content)
            for uc_id in set(referenced_uc_ids):
                if uc_id not in all_uc_ids:
                    warnings.append(
                        f"警告: {file_path.relative_to(PROJECT_ROOT)} で参照されている "
                        f"ユースケースID {uc_id} がユースケース記述に存在しません"
                    )
        except Exception:
            pass
    
    return warnings


def main():
    """
    メイン処理
    """
    print("=" * 60)
    print("工程1（要件定義）成果物チェック")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # 1. ファイル存在確認
    print("1. ファイル存在確認...")
    file_errors, existing_files = check_file_existence()
    errors.extend(file_errors)
    
    if file_errors:
        for error in file_errors:
            print(f"  ❌ {error}")
    else:
        print("  ✅ すべての必須ファイルが存在します")
    print()
    
    # 2. ID重複チェック
    print("2. ID重複チェック...")
    dup_errors = check_id_duplicates()
    errors.extend(dup_errors)
    
    if dup_errors:
        for error in dup_errors:
            print(f"  ❌ {error}")
    else:
        print("  ✅ IDの重複はありません")
    print()
    
    # 3. 相互参照チェック
    print("3. 相互参照チェック...")
    ref_warnings = check_cross_references()
    warnings.extend(ref_warnings)
    
    if ref_warnings:
        for warning in ref_warnings:
            print(f"  ⚠️  {warning}")
    else:
        print("  ✅ 相互参照に問題はありません")
    print()
    
    # 結果出力
    result = {
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
        "timestamp": datetime.now().isoformat(),
        "phase": "01",
    }
    
    # 結果ファイル出力
    result_file = PROJECT_ROOT / ".github" / "checks" / "common" / "phase-01-result.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # サマリー表示
    print("=" * 60)
    print("チェック結果")
    print("=" * 60)
    print(f"ステータス: {'❌ FAIL' if errors else '✅ PASS'}")
    print(f"エラー数: {len(errors)}")
    print(f"警告数: {len(warnings)}")
    print()
    print(f"結果ファイル: {result_file.relative_to(PROJECT_ROOT)}")
    print("=" * 60)
    
    # 終了コード
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
