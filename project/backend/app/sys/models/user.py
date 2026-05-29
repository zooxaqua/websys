"""ユーザーモデル"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """ユーザーエンティティ"""
    
    id: str
    username: str = Field(min_length=3, max_length=50)
    passwordHash: str
    displayName: str = Field(min_length=1, max_length=100)
    role: str = Field(pattern="^(admin|user)$")
    email: EmailStr
    metadata: dict = Field(default_factory=dict)
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None
    
    def validate_password(self, password: str) -> bool:
        """パスワードを検証"""
        from ..core.security import verify_password
        return verify_password(password, self.passwordHash)
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump(mode="json")
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """辞書からインスタンスを生成"""
        return cls(**data)


class UserCreate(BaseModel):
    """ユーザー作成リクエスト"""
    
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    displayName: str = Field(min_length=1, max_length=100)
    role: str = Field(pattern="^(admin|user)$")
    email: EmailStr
    metadata: dict = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """ユーザー更新リクエスト"""
    
    displayName: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    email: Optional[EmailStr] = None
    metadata: Optional[dict] = None


class UserResponse(BaseModel):
    """ユーザーレスポンス（パスワードハッシュを除外）"""
    
    id: str
    username: str
    displayName: str
    role: str
    email: str
    createdAt: datetime
    updatedAt: datetime
    lastLogin: Optional[datetime] = None
    metadata: dict = Field(default_factory=dict)
