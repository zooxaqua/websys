#!/usr/bin/env python3
"""
工程3（詳細設計）チェックプログラム

チェック項目:
1. 必須ファイルの存在確認（システム共通基盤5ファイル + TODOアプリ5ファイル）
2. クラス名の整合性チェック
3. エラーコードの整合性チェック
4. mermaid図の基本構文チェック
5. トレーサビリティチェック（工程2参照の記載）

出力:
- .github/checks/common/phase-03-result.json
  - status: "pass" or "fail"
  - errors: エラーリスト
  - warnings: 警告リスト
  - timestamp: チェック実行日時
  - phase: "03"

終了コード:
- 0: チェック合格
- 1: チェック不合格
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# プロジェクトルート
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# チェック対象ファイル
REQUIRED_FILES_SYS = [
    "documents/sys/03-detail-design/class-design.md",
    "documents/sys/03-detail-design/sequence-diagrams.md",
    "documents/sys/03-detail-design/database-schema.md",
    "documents/sys/03-detail-design/error-handling.md",
    "documents/sys/03-detail-design/test-cases.md",
]

REQUIRED_FILES_APP = [
    "documents/app/03-detail-design/class-design.md",
    "documents/app/03-detail-design/sequence-diagrams.md",
    "documents/app/03-detail-design/database-schema.md",
    "documents/app/03-detail-design/error-handling.md",
    "documents/app/03-detail-design/test-cases.md",
]

# エラー・警告リスト
errors: List[str] = []
warnings: List[str] = []


def check_file_exists(file_path: str) -> bool:
    """ファイル存在確認"""
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        errors.append(f"必須ファイルが見つかりません: {file_path}")
        return False
    return True


def check_class_names(file_path: str, expected_classes: List[str]) -> None:
    """クラス名の存在確認"""
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        return
    
    content = full_path.read_text(encoding="utf-8")
    
    for class_name in expected_classes:
        if class_name not in content:
            warnings.append(f"{file_path}: クラス名 '{class_name}' が見つかりません")


def check_error_codes(file_path: str, expected_error_codes: List[str]) -> None:
    """エラーコードの存在確認"""
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        return
    
    content = full_path.read_text(encoding="utf-8")
    
    for error_code in expected_error_codes:
        if error_code not in content:
            warnings.append(f"{file_path}: エラーコード '{error_code}' が見つかりません")


def check_mermaid_diagrams(file_path: str) -> None:
    """mermaid図の基本構文チェック"""
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        return
    
    content = full_path.read_text(encoding="utf-8")
    
    # mermaidブロックの存在確認
    if "```mermaid" not in content:
        warnings.append(f"{file_path}: mermaid図が見つかりません")
        return
    
    # 基本的な構文チェック（sequenceDiagram, flowchart, classDiagram）
    mermaid_blocks = []
    in_mermaid = False
    current_block = []
    
    for line in content.split("\n"):
        if "```mermaid" in line:
            in_mermaid = True
            current_block = []
        elif in_mermaid and "```" in line:
            in_mermaid = False
            mermaid_blocks.append("\n".join(current_block))
        elif in_mermaid:
            current_block.append(line)
    
    for i, block in enumerate(mermaid_blocks, 1):
        if not any(keyword in block for keyword in ["sequenceDiagram", "flowchart", "classDiagram", "graph"]):
            warnings.append(f"{file_path}: mermaidブロック{i}に有効なダイアグラムタイプが見つかりません")


def check_traceability(file_path: str, required_references: List[str]) -> None:
    """トレーサビリティチェック（工程2の参照確認）"""
    full_path = PROJECT_ROOT / file_path
    if not full_path.exists():
        return
    
    content = full_path.read_text(encoding="utf-8")
    
    for reference in required_references:
        if reference not in content:
            warnings.append(f"{file_path}: トレーサビリティ '{reference}' が見つかりません")


def run_checks() -> Tuple[str, List[str], List[str]]:
    """全チェック実行"""
    print("=== 工程3（詳細設計）チェック開始 ===\n")
    
    # 1. 必須ファイルの存在確認
    print("1. 必須ファイルの存在確認")
    all_files_exist = True
    
    for file_path in REQUIRED_FILES_SYS:
        if not check_file_exists(file_path):
            all_files_exist = False
    
    for file_path in REQUIRED_FILES_APP:
        if not check_file_exists(file_path):
            all_files_exist = False
    
    if all_files_exist:
        print("   ✓ 全ての必須ファイルが存在します\n")
    else:
        print("   ✗ 必須ファイルが不足しています\n")
    
    # 2. システム共通基盤のクラス名チェック
    print("2. システム共通基盤のクラス名チェック")
    check_class_names(
        "documents/sys/03-detail-design/class-design.md",
        [
            "User", "App", "Notification", "Session",
            "JWTService", "AuthService", "UserService", "AppService", "NotificationService",
            "BaseDAL", "JsonDAL", "UserDAL", "AppDAL", "NotificationDAL", "SessionDAL"
        ]
    )
    print("   ✓ クラス名チェック完了\n")
    
    # 3. TODOアプリのクラス名チェック
    print("3. TODOアプリのクラス名チェック")
    check_class_names(
        "documents/app/03-detail-design/class-design.md",
        ["Todo", "TodoService", "TodoDAL"]
    )
    print("   ✓ クラス名チェック完了\n")
    
    # 4. システム共通基盤のエラーコードチェック
    print("4. システム共通基盤のエラーコードチェック")
    sys_error_codes = [
        "ERR-SYS-AUTH-001", "ERR-SYS-AUTH-002", "ERR-SYS-AUTH-003",
        "ERR-SYS-USER-001", "ERR-SYS-USER-002",
        "ERR-SYS-APPS-001", "ERR-SYS-APPS-002",
        "ERR-SYS-NOTF-001",
        "ERR-SYS-VALD-001",
        "ERR-SYS-SERV-001", "ERR-SYS-SERV-002"
    ]
    check_error_codes("documents/sys/03-detail-design/error-handling.md", sys_error_codes)
    print("   ✓ エラーコードチェック完了\n")
    
    # 5. TODOアプリのエラーコードチェック
    print("5. TODOアプリのエラーコードチェック")
    app_error_codes = [
        "ERR-TODO-001", "ERR-TODO-002", "ERR-TODO-003",
        "ERR-TODO-004", "ERR-TODO-005", "ERR-TODO-006"
    ]
    check_error_codes("documents/app/03-detail-design/error-handling.md", app_error_codes)
    print("   ✓ エラーコードチェック完了\n")
    
    # 6. シーケンス図のmermaid構文チェック
    print("6. シーケンス図のmermaid構文チェック")
    check_mermaid_diagrams("documents/sys/03-detail-design/sequence-diagrams.md")
    check_mermaid_diagrams("documents/app/03-detail-design/sequence-diagrams.md")
    print("   ✓ mermaid図チェック完了\n")
    
    # 7. トレーサビリティチェック（工程2の参照）
    print("7. トレーサビリティチェック")
    for file_path in REQUIRED_FILES_SYS:
        check_traceability(file_path, ["工程2", "基本設計"])
    for file_path in REQUIRED_FILES_APP:
        check_traceability(file_path, ["工程2", "基本設計"])
    print("   ✓ トレーサビリティチェック完了\n")
    
    # 結果判定
    if errors:
        status = "fail"
        print("=== チェック結果: 不合格 ===")
        print(f"エラー: {len(errors)}件")
        for error in errors:
            print(f"  - {error}")
    else:
        status = "pass"
        print("=== チェック結果: 合格 ===")
    
    if warnings:
        print(f"\n警告: {len(warnings)}件")
        for warning in warnings:
            print(f"  - {warning}")
    
    return status, errors, warnings


def write_result(status: str, errors: List[str], warnings: List[str]) -> None:
    """結果をJSONファイルに出力"""
    result = {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "phase": "03"
    }
    
    result_file = PROJECT_ROOT / ".github/checks/common/phase-03-result.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n結果ファイル: {result_file}")


def main() -> int:
    """メイン処理"""
    status, errors, warnings = run_checks()
    write_result(status, errors, warnings)
    
    # 終了コード: 0（成功）/ 1（失敗）
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
