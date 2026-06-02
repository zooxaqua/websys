"""
単体テスト: TODO Service

テスト対象: project/apps/todo-app/backend/app/services/todo_service.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "apps" / "todo-app" / "backend"))

from app.services.todo_service import TodoService
from app.models.todo import TodoCreate, TodoUpdate
from fastapi import HTTPException


class TestTodoService:
    """TodoService のテストクラス"""
    
    @pytest.fixture
    def todo_dal_mock(self):
        """TodoDAL のモック"""
        return Mock()
    
    @pytest.fixture
    def todo_service(self, todo_dal_mock):
        """TodoService インスタンス"""
        return TodoService(todo_dal_mock)
    
    @pytest.fixture
    def valid_todo_data(self):
        """有効なTODOデータ"""
        return {
            "id": "todo-001",
            "userId": "user-001",
            "title": "Test TODO",
            "description": "Test",
            "dueDate": datetime.utcnow().isoformat() + "Z",
            "completed": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    
    # TC-TODO-SVC-001: 正常系 - TODO一覧取得
    def test_list_todos_success(self, todo_service, todo_dal_mock, valid_todo_data):
        """TODO一覧取得成功"""
        todo_dal_mock.find_by_user.return_value = [valid_todo_data]
        todo_dal_mock.count_by_user.return_value = 1
        
        todos, total = todo_service.list_todos("user-001")
        
        assert len(todos) == 1
        assert total == 1
    
    # TC-TODO-SVC-002: 正常系 - TODO詳細取得
    def test_get_todo_success(self, todo_service, todo_dal_mock, valid_todo_data):
        """TODO詳細取得成功"""
        todo_dal_mock.find_one.return_value = valid_todo_data
        
        todo = todo_service.get_todo("todo-001", "user-001")
        
        assert todo.id == "todo-001"
    
    # TC-TODO-SVC-003: 異常系 - TODO存在しない
    def test_get_todo_not_found(self, todo_service, todo_dal_mock):
        """TODO存在しない"""
        todo_dal_mock.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            todo_service.get_todo("nonexistent", "user-001")
        
        assert exc.value.status_code == 404
    
    # TC-TODO-SVC-004: 異常系 - 権限エラー
    def test_get_todo_forbidden(self, todo_service, todo_dal_mock, valid_todo_data):
        """権限エラー"""
        todo_dal_mock.find_one.return_value = valid_todo_data
        
        with pytest.raises(HTTPException) as exc:
            todo_service.get_todo("todo-001", "other-user")
        
        assert exc.value.status_code == 403
    
    # TC-TODO-SVC-005: 正常系 - TODO作成
    def test_create_todo_success(self, todo_service, todo_dal_mock):
        """TODO作成成功"""
        todo_dal_mock.insert.return_value = True
        
        todo_create = TodoCreate(title="New TODO", description="Test")
        
        todo = todo_service.create_todo("user-001", todo_create)
        
        assert todo.title == "New TODO"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
