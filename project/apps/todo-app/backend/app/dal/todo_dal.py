"""TODO DAL"""
import sys
from pathlib import Path

# システム共通基盤のDALをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "backend"))

from app.sys.dal.json_dal import JsonDAL
from typing import Optional


class TodoDAL(JsonDAL):
    """TODO専用DAL"""
    
    collection_name = "todos"
    
    def __init__(self):
        # アプリ固有のdataディレクトリを使用
        data_dir = Path(__file__).parent.parent.parent / "data"
        super().__init__(data_dir=str(data_dir))
    
    def find_by_user(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "createdAt",
        order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> list[dict]:
        """ユーザーのTODOを検索"""
        all_data = self._load_data()
        
        results = []
        for todo_id, todo in all_data.items():
            # ユーザーフィルタ
            if todo.get("userId") != user_id:
                continue
            
            # 完了状態フィルタ
            if completed is not None and todo.get("completed") != completed:
                continue
            
            # 検索フィルタ
            if search:
                search_lower = search.lower()
                title = todo.get("title", "").lower()
                description = todo.get("description", "").lower()
                if search_lower not in title and search_lower not in description:
                    continue
            
            results.append(todo)
        
        # ソート
        reverse = (order == "desc")
        results.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
        
        # ページング
        return results[offset:offset + limit]
    
    def count_by_user(self, user_id: str, completed: Optional[bool] = None) -> int:
        """ユーザーのTODO数をカウント"""
        all_data = self._load_data()
        
        count = 0
        for todo_id, todo in all_data.items():
            if todo.get("userId") != user_id:
                continue
            
            if completed is not None and todo.get("completed") != completed:
                continue
            
            count += 1
        
        return count
    
    def count_overdue(self, user_id: str) -> int:
        """期限切れTODO数をカウント"""
        from datetime import datetime
        
        all_data = self._load_data()
        now = datetime.utcnow()
        
        count = 0
        for todo_id, todo in all_data.items():
            if todo.get("userId") != user_id:
                continue
            
            if todo.get("completed"):
                continue
            
            due_date_str = todo.get("dueDate")
            if not due_date_str:
                continue
            
            due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
            if due_date < now:
                count += 1
        
        return count
