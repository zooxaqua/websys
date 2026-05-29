"""TODOサービス"""
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException, status
import uuid
from ..models.todo import Todo, TodoCreate, TodoUpdate
from ..dal.todo_dal import TodoDAL


class TodoService:
    """TODOビジネスロジック"""
    
    def __init__(self, dal: TodoDAL):
        self.dal = dal
    
    def list_todos(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "createdAt",
        order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[list[Todo], int]:
        """TODO一覧を取得"""
        todo_data_list = self.dal.find_by_user(
            user_id=user_id,
            completed=completed,
            search=search,
            sort_by=sort_by,
            order=order,
            limit=limit,
            offset=offset
        )
        
        todos = [Todo.from_dict(data) for data in todo_data_list]
        total = self.dal.count_by_user(user_id, completed)
        
        return todos, total
    
    def get_todo(self, todo_id: str, user_id: str) -> Todo:
        """TODO詳細を取得"""
        todo_data = self.dal.find_one({"id": todo_id})
        if not todo_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-APP-TODO-001", "message": "TODOが見つかりません"}
            )
        
        # 権限チェック
        if todo_data["userId"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ERR-APP-TODO-002", "message": "このTODOにアクセスする権限がありません"}
            )
        
        return Todo.from_dict(todo_data)
    
    def create_todo(self, user_id: str, todo_create: TodoCreate) -> Todo:
        """TODOを作成"""
        # バリデーション
        is_valid, error_msg = self.validate_todo_data(todo_create.model_dump())
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": error_msg}
            )
        
        now = datetime.utcnow()
        
        todo_data = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "title": todo_create.title,
            "description": todo_create.description,
            "dueDate": todo_create.dueDate,
            "completed": False,
            "createdAt": now.isoformat() + "Z",
            "updatedAt": now.isoformat() + "Z"
        }
        
        self.dal.insert(todo_data)
        return Todo.from_dict(todo_data)
    
    def update_todo(self, todo_id: str, user_id: str, todo_update: TodoUpdate) -> Todo:
        """TODOを更新"""
        # TODO存在確認と権限チェック
        todo = self.get_todo(todo_id, user_id)
        
        # 更新データ作成
        update_data = todo_update.model_dump(exclude_unset=True)
        update_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        
        self.dal.update(todo_id, update_data)
        
        # 更新後のデータを取得
        updated_data = self.dal.find_one({"id": todo_id})
        return Todo.from_dict(updated_data)
    
    def delete_todo(self, todo_id: str, user_id: str) -> bool:
        """TODOを削除"""
        # TODO存在確認と権限チェック
        self.get_todo(todo_id, user_id)
        
        return self.dal.delete(todo_id)
    
    def toggle_todo(self, todo_id: str, user_id: str) -> Todo:
        """TODO完了/未完了を切り替え"""
        todo = self.get_todo(todo_id, user_id)
        
        new_completed = not todo.completed
        update_data = {
            "completed": new_completed,
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }
        
        self.dal.update(todo_id, update_data)
        
        # 更新後のデータを取得
        updated_data = self.dal.find_one({"id": todo_id})
        return Todo.from_dict(updated_data)
    
    def get_stats(self, user_id: str) -> dict:
        """TODO統計情報を取得"""
        total = self.dal.count_by_user(user_id)
        completed = self.dal.count_by_user(user_id, completed=True)
        active = self.dal.count_by_user(user_id, completed=False)
        overdue = self.dal.count_overdue(user_id)
        
        return {
            "total": total,
            "completed": completed,
            "active": active,
            "overdue": overdue
        }
    
    def validate_todo_data(self, data: dict) -> Tuple[bool, str]:
        """TODOデータをバリデーション"""
        # タイトルチェック
        title = data.get("title", "")
        if not title:
            return False, "タイトルは必須です"
        
        if len(title) > 100:
            return False, "タイトルは100文字以内である必要があります"
        
        # 説明チェック
        description = data.get("description", "")
        if len(description) > 500:
            return False, "説明は500文字以内である必要があります"
        
        return True, ""
