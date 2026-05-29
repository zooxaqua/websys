"""TODOモデル"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Todo(BaseModel):
    """TODOエンティティ"""
    
    id: str
    userId: str
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    dueDate: Optional[str] = None
    completed: bool = False
    createdAt: datetime
    updatedAt: datetime
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump(mode="json")
    
    def is_overdue(self) -> bool:
        """期限切れか判定"""
        if self.completed or not self.dueDate:
            return False
        
        due_date = datetime.fromisoformat(self.dueDate.replace("Z", "+00:00"))
        return due_date < datetime.utcnow()
    
    def toggle_completed(self) -> None:
        """完了状態を反転"""
        self.completed = not self.completed
        self.updatedAt = datetime.utcnow()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """辞書からインスタンスを生成"""
        return cls(**data)


class TodoCreate(BaseModel):
    """TODO作成リクエスト"""
    
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    dueDate: Optional[str] = None


class TodoUpdate(BaseModel):
    """TODO更新リクエスト"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    dueDate: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    """TODOレスポンス"""
    
    id: str
    userId: str
    title: str
    description: str
    dueDate: Optional[str]
    completed: bool
    createdAt: datetime
    updatedAt: datetime
