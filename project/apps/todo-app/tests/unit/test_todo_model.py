"""
単体テスト: TODO Model

テスト対象: project/apps/todo-app/backend/app/models/todo.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "apps" / "todo-app" / "backend"))

from app.models.todo import Todo, TodoCreate, TodoUpdate


class TestTodoModel:
    """Todo モデルのテストクラス"""
    
    @pytest.fixture
    def valid_todo_data(self):
        """有効なTODOデータ"""
        return {
            "id": "todo-001",
            "userId": "user-001",
            "title": "Test TODO",
            "description": "Test description",
            "dueDate": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
            "completed": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
    
    # TC-TODO-MODEL-001: 正常系 - TODO作成
    def test_todo_creation(self, valid_todo_data):
        """TODO作成成功"""
        todo = Todo(**valid_todo_data)
        
        assert todo.id == "todo-001"
        assert todo.title == "Test TODO"
        assert todo.completed is False
    
    # TC-TODO-MODEL-002: 正常系 - 辞書変換
    def test_to_dict(self, valid_todo_data):
        """辞書変換"""
        todo = Todo(**valid_todo_data)
        
        todo_dict = todo.to_dict()
        
        assert todo_dict["id"] == "todo-001"
        assert todo_dict["title"] == "Test TODO"
    
    # TC-TODO-MODEL-003: 正常系 - 期限切れ判定（期限内）
    def test_is_overdue_not_overdue(self, valid_todo_data):
        """期限切れ判定（期限内）"""
        todo = Todo(**valid_todo_data)
        
        assert todo.is_overdue() is False
    
    # TC-TODO-MODEL-004: 正常系 - 期限切れ判定（期限切れ）
    def test_is_overdue_overdue(self, valid_todo_data):
        """期限切れ判定（期限切れ）"""
        valid_todo_data["dueDate"] = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
        todo = Todo(**valid_todo_data)
        
        assert todo.is_overdue() is True
    
    # TC-TODO-MODEL-005: 正常系 - 完了状態切り替え
    def test_toggle_completed(self, valid_todo_data):
        """完了状態切り替え"""
        todo = Todo(**valid_todo_data)
        
        assert todo.completed is False
        todo.toggle_completed()
        assert todo.completed is True
        todo.toggle_completed()
        assert todo.completed is False
    
    # TC-TODO-MODEL-006: 境界値 - タイトル最小長（1文字）
    def test_title_min_length(self, valid_todo_data):
        """タイトル最小長（1文字）"""
        valid_todo_data["title"] = "A"
        todo = Todo(**valid_todo_data)
        
        assert todo.title == "A"
    
    # TC-TODO-MODEL-007: 境界値 - タイトル最大長（100文字）
    def test_title_max_length(self, valid_todo_data):
        """タイトル最大長（100文字）"""
        valid_todo_data["title"] = "A" * 100
        todo = Todo(**valid_todo_data)
        
        assert len(todo.title) == 100
    
    # TC-TODO-MODEL-008: 異常系 - タイトル空文字
    def test_title_empty(self, valid_todo_data):
        """タイトル空文字"""
        valid_todo_data["title"] = ""
        
        with pytest.raises(Exception):  # ValidationError
            Todo(**valid_todo_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
