"""セッションモデル"""
from datetime import datetime
from pydantic import BaseModel, Field


class Session(BaseModel):
    """セッションエンティティ"""
    
    sessionId: str
    userId: str
    token: str
    createdAt: datetime
    expiresAt: datetime
    metadata: dict = Field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """セッションが有効か"""
        return datetime.utcnow() < self.expiresAt
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump(mode="json")
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """辞書からインスタンスを生成"""
        return cls(**data)
