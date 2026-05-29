"""DAL 抽象クラス"""
from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseDAL(ABC):
    """データアクセス層の抽象基底クラス"""
    
    collection_name: str
    
    @abstractmethod
    def find(self, criteria: dict, limit: int = 100, offset: int = 0) -> list[dict]:
        """条件に一致するレコードを検索"""
        pass
    
    @abstractmethod
    def find_one(self, criteria: dict) -> Optional[dict]:
        """条件に一致する単一レコードを検索"""
        pass
    
    @abstractmethod
    def insert(self, data: dict) -> str:
        """レコードを挿入"""
        pass
    
    @abstractmethod
    def update(self, id: str, data: dict) -> bool:
        """レコードを更新"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """レコードを削除"""
        pass
    
    @abstractmethod
    def count(self, criteria: dict) -> int:
        """条件に一致するレコード数をカウント"""
        pass
    
    @abstractmethod
    def exists(self, criteria: dict) -> bool:
        """条件に一致するレコードが存在するか"""
        pass
