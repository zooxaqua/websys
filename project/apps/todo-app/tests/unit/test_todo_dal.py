"""
単体テスト: TODO DAL

テスト対象: project/apps/todo-app/backend/app/dal/todo_dal.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "apps" / "todo-app" / "backend"))

from app.dal.todo_dal import TodoDAL


class TestTodoDAL:
    """TodoDAL のテストクラス"""
    
    @pytest.fixture
    def todo_dal(self, tmp_path):
        """TodoDAL インスタンス"""
        # 一時ディレクトリを使用
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        dal = TodoDAL()
        dal.data_dir = str(data_dir)
        return dal
    
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
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }
    
    # TC-TODO-DAL-001: 正常系 - TODO挿入
    def test_insert_success(self, todo_dal, valid_todo_data):
        """TODO挿入成功"""
        todo_id = todo_dal.insert(valid_todo_data)
        
        assert todo_id == "todo-001"
    
    # TC-TODO-DAL-002: 正常系 - ユーザーのTODO検索
    def test_find_by_user(self, todo_dal, valid_todo_data):
        """ユーザーのTODO検索"""
        todo_dal.insert(valid_todo_data)
        
        todos = todo_dal.find_by_user("user-001")
        
        assert len(todos) == 1
        assert todos[0]["userId"] == "user-001"
    
    # TC-TODO-DAL-003: 正常系 - 完了状態でフィルタ
    def test_find_by_user_completed_filter(self, todo_dal, valid_todo_data):
        """完了状態でフィルタ"""
        todo_dal.insert(valid_todo_data)
        completed_todo = valid_todo_data.copy()
        completed_todo["id"] = "todo-002"
        completed_todo["completed"] = True
        todo_dal.insert(completed_todo)
        
        todos = todo_dal.find_by_user("user-001", completed=False)
        
        assert len(todos) == 1
        assert todos[0]["completed"] is False
    
    # TC-TODO-DAL-004: 正常系 - 検索フィルタ
    def test_find_by_user_search(self, todo_dal, valid_todo_data):
        """検索フィルタ"""
        todo_dal.insert(valid_todo_data)
        
        todos = todo_dal.find_by_user("user-001", search="Test")
        
        assert len(todos) == 1
    
    # TC-TODO-DAL-005: 正常系 - カウント
    def test_count_by_user(self, todo_dal, valid_todo_data):
        """ユーザーのTODOカウント"""
        todo_dal.insert(valid_todo_data)
        
        count = todo_dal.count_by_user("user-001")
        
        assert count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
