"""通知モデル"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Notification(BaseModel):
    """通知エンティティ"""
    
    id: str
    userId: str
    type: str = Field(pattern="^(info|warning|error|success)$")
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)
    metadata: dict = Field(default_factory=dict)
    read: bool = False
    createdAt: datetime
    expiresAt: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump(mode="json")
    
    def is_expired(self) -> bool:
        """期限切れか判定"""
        if not self.expiresAt:
            return False
        return datetime.utcnow() > self.expiresAt
    
    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """辞書からインスタンスを生成"""
        return cls(**data)


class NotificationCreate(BaseModel):
    """通知作成リクエスト"""
    
    type: str = Field(pattern="^(info|warning|error|success)$")
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)
    metadata: dict = Field(default_factory=dict)
    expiresAt: Optional[datetime] = None


class NotificationResponse(BaseModel):
    """通知レスポンス"""
    
    id: str
    userId: str
    type: str
    title: str
    message: str
    metadata: dict
    read: bool
    createdAt: datetime
    expiresAt: Optional[datetime] = None
