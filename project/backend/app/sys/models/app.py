"""アプリモデル"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class App(BaseModel):
    """アプリエンティティ"""
    
    id: str
    name: str
    version: str
    description: str
    icon: str
    entryPoint: str
    apiPrefix: str
    enabled: bool = True
    author: str
    requiredPermissions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    manifest: dict = Field(default_factory=dict)
    lastUpdated: datetime
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return self.model_dump(mode="json")
    
    def validate_manifest(self) -> bool:
        """マニフェストの妥当性を検証"""
        required_fields = ["name", "version", "displayName", "entryPoint", "apiPrefix"]
        return all(field in self.manifest for field in required_fields)
    
    @classmethod
    def from_dict(cls, data: dict) -> "App":
        """辞書からインスタンスを生成"""
        return cls(**data)


class AppResponse(BaseModel):
    """アプリレスポンス"""
    
    id: str
    name: str
    version: str
    description: str
    icon: str
    entryPoint: str
    apiPrefix: str
    enabled: bool
    author: str
    lastUpdated: datetime
