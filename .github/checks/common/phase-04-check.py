#!/usr/bin/env python3
"""
工程4: コーディング チェックプログラム

責務: 実装ファイルの存在確認、構文チェック、コーディング規約チェック

実行方法:
    python .github/checks/common/phase-04-check.py

出力:
    .github/checks/common/phase-04-result.json

検証項目:
    1. 実装ファイルの存在確認（詳細設計に対応）
    2. Python 構文エラーチェック
    3. Import 順序チェック（標準ライブラリ → サードパーティ → ローカル）
    4. TODO/FIXME コメントの検出
    5. セキュリティパターンチェック
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class Phase04Checker:
    """工程4チェッカー"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.root_dir = Path(__file__).parent.parent.parent.parent
        
    def run(self) -> Dict[str, Any]:
        """チェック実行"""
        print("工程4: コーディング チェックを開始します...")
        
        # 1. システム共通基盤バックエンドの存在確認
        self.check_system_backend_files()
        
        # 2. TODOアプリバックエンドの存在確認
        self.check_todo_app_backend_files()
        
        # 3. フロントエンドの存在確認
        self.check_frontend_files()
        
        # 4. Python構文チェック
        self.check_python_syntax()
        
        # 5. コーディング規約チェック
        self.check_coding_standards()
        
        # 6. TODO/FIXMEコメントチェック
        self.check_todo_comments()
        
        # 結果を返す
        status = "pass" if len(self.errors) == 0 else "fail"
        
        result = {
            "status": status,
            "phase": "04",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "errorCount": len(self.errors),
                "warningCount": len(self.warnings)
            }
        }
        
        return result
    
    def check_system_backend_files(self):
        """システム共通基盤バックエンドファイル存在確認"""
        print("  ✓ システム共通基盤バックエンドファイルをチェック中...")
        
        required_files = [
            # models
            "project/backend/app/sys/models/user.py",
            "project/backend/app/sys/models/app.py",
            "project/backend/app/sys/models/notification.py",
            "project/backend/app/sys/models/session.py",
            # dal
            "project/backend/app/sys/dal/base_dal.py",
            "project/backend/app/sys/dal/json_dal.py",
            "project/backend/app/sys/dal/user_dal.py",
            "project/backend/app/sys/dal/app_dal.py",
            "project/backend/app/sys/dal/notification_dal.py",
            "project/backend/app/sys/dal/session_dal.py",
            # services
            "project/backend/app/sys/services/jwt_service.py",
            "project/backend/app/sys/services/auth_service.py",
            "project/backend/app/sys/services/user_service.py",
            "project/backend/app/sys/services/app_service.py",
            "project/backend/app/sys/services/notification_service.py",
            # api
            "project/backend/app/sys/api/auth.py",
            "project/backend/app/sys/api/users.py",
            "project/backend/app/sys/api/apps.py",
            "project/backend/app/sys/api/notifications.py",
            "project/backend/app/sys/api/config.py",
            "project/backend/app/sys/api/health.py",
            # core
            "project/backend/app/sys/core/config.py",
            "project/backend/app/sys/core/dependencies.py",
            "project/backend/app/sys/core/middleware.py",
            "project/backend/app/sys/core/exceptions.py",
            # main
            "project/backend/app/main.py",
            # data
            "project/backend/data/users.json",
            "project/backend/data/apps.json",
            "project/backend/data/config.json",
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                self.errors.append(f"必須ファイルが見つかりません: {file_path}")
    
    def check_todo_app_backend_files(self):
        """TODOアプリバックエンドファイル存在確認"""
        print("  ✓ TODOアプリバックエンドファイルをチェック中...")
        
        required_files = [
            "project/apps/todo-app/manifest.json",
            "project/apps/todo-app/backend/app/models/todo.py",
            "project/apps/todo-app/backend/app/dal/todo_dal.py",
            "project/apps/todo-app/backend/app/services/todo_service.py",
            "project/apps/todo-app/backend/app/api/todos.py",
            "project/apps/todo-app/backend/app/main.py",
            "project/apps/todo-app/backend/data/todos.json",
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                self.errors.append(f"必須ファイルが見つかりません: {file_path}")
    
    def check_frontend_files(self):
        """フロントエンドファイル存在確認"""
        print("  ✓ フロントエンドファイルをチェック中...")
        
        required_files = [
            "project/frontend/src/sys/utils/fetch.ts",
            "project/frontend/src/sys/utils/validation.ts",
            "project/frontend/src/sys/utils/storage.ts",
            "project/frontend/src/sys/api/auth.ts",
            "project/frontend/src/sys/api/users.ts",
            "project/frontend/src/sys/api/apps.ts",
            "project/frontend/src/sys/api/notifications.ts",
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                self.errors.append(f"必須ファイルが見つかりません: {file_path}")
    
    def check_python_syntax(self):
        """Python構文エラーチェック"""
        print("  ✓ Python構文エラーをチェック中...")
        
        python_files = []
        
        # project/backend/app/sys/ 配下
        sys_dir = self.root_dir / "project" / "backend" / "app" / "sys"
        if sys_dir.exists():
            python_files.extend(sys_dir.rglob("*.py"))
        
        # project/backend/app/main.py
        main_py = self.root_dir / "project" / "backend" / "app" / "main.py"
        if main_py.exists():
            python_files.append(main_py)
        
        # project/apps/todo-app/ 配下
        todo_app_dir = self.root_dir / "project" / "apps" / "todo-app" / "backend" / "app"
        if todo_app_dir.exists():
            python_files.extend(todo_app_dir.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, str(py_file), 'exec')
            except SyntaxError as e:
                self.errors.append(
                    f"構文エラー: {py_file.relative_to(self.root_dir)} "
                    f"(行 {e.lineno}): {e.msg}"
                )
            except Exception as e:
                self.warnings.append(
                    f"ファイル読み込みエラー: {py_file.relative_to(self.root_dir)}: {str(e)}"
                )
    
    def check_coding_standards(self):
        """コーディング規約チェック"""
        print("  ✓ コーディング規約をチェック中...")
        
        python_files = []
        
        # project/backend/app/sys/ 配下
        sys_dir = self.root_dir / "project" / "backend" / "app" / "sys"
        if sys_dir.exists():
            python_files.extend(sys_dir.rglob("*.py"))
        
        # project/apps/todo-app/ 配下
        todo_app_dir = self.root_dir / "project" / "apps" / "todo-app" / "backend" / "app"
        if todo_app_dir.exists():
            python_files.extend(todo_app_dir.rglob("*.py"))
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    # Import順序チェック（簡易版）
                    imports = []
                    for i, line in enumerate(lines, 1):
                        if line.strip().startswith(('import ', 'from ')):
                            imports.append((i, line.strip()))
                    
                    # 標準ライブラリ → サードパーティ → ローカル の順序確認
                    # （簡易実装: 相対importが先に来ていないかのみチェック）
                    found_local = False
                    for line_no, import_line in imports:
                        if import_line.startswith('from .'):
                            found_local = True
                        elif found_local and not import_line.startswith('from .'):
                            self.warnings.append(
                                f"Import順序: {py_file.relative_to(self.root_dir)} "
                                f"(行 {line_no}): ローカルimportの後に非ローカルimportがあります"
                            )
                            break
                    
                    # セキュリティパターンチェック
                    content = ''.join(lines)
                    
                    # パスワードのハードコード検出
                    if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                        self.warnings.append(
                            f"セキュリティ: {py_file.relative_to(self.root_dir)}: "
                            "パスワードがハードコードされている可能性があります"
                        )
                    
            except Exception as e:
                self.warnings.append(
                    f"ファイル読み込みエラー: {py_file.relative_to(self.root_dir)}: {str(e)}"
                )
    
    def check_todo_comments(self):
        """TODO/FIXMEコメント検出"""
        print("  ✓ TODO/FIXMEコメントをチェック中...")
        
        all_files = []
        
        # Python files
        sys_dir = self.root_dir / "project" / "backend" / "app" / "sys"
        if sys_dir.exists():
            all_files.extend(sys_dir.rglob("*.py"))
        
        todo_app_dir = self.root_dir / "project" / "apps" / "todo-app" / "backend" / "app"
        if todo_app_dir.exists():
            all_files.extend(todo_app_dir.rglob("*.py"))
        
        # TypeScript files
        frontend_sys_dir = self.root_dir / "project" / "frontend" / "src" / "sys"
        if frontend_sys_dir.exists():
            all_files.extend(frontend_sys_dir.rglob("*.ts"))
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if re.search(r'\bTODO\b|\bFIXME\b', line, re.IGNORECASE):
                            self.warnings.append(
                                f"TODO/FIXMEコメント: {file_path.relative_to(self.root_dir)} "
                                f"(行 {i}): {line.strip()}"
                            )
            except Exception:
                pass


def main():
    """メイン処理"""
    checker = Phase04Checker()
    result = checker.run()
    
    # 結果をJSON出力
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "phase-04-result.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果を {output_file} に出力しました")
    print(f"ステータス: {result['status']}")
    print(f"エラー: {result['summary']['errorCount']}件")
    print(f"警告: {result['summary']['warningCount']}件")
    
    # エラーがあれば終了コード1
    sys.exit(0 if result['status'] == 'pass' else 1)


if __name__ == "__main__":
    main()
