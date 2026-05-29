"""
基底データアクセス層（抽象クラス）

このモジュールはDAL（Data Access Layer）の抽象基底クラスを定義します。
すべてのDALクラスはこのクラスを継承し、統一的なインターフェースを提供します。
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseDAL(ABC):
    """
    データアクセス層の抽象基底クラス
    
    すべてのDAL実装はこのクラスを継承し、CRUD操作の統一インターフェースを提供します。
    将来的にJSON DBからRDBへの移行時も、このインターフェースを維持することで
    透過的な切り替えを実現します。
    """
    
    # サブクラスで定義するコレクション名
    collection_name: str = ""
    
    @abstractmethod
    def find(
        self,
        criteria: dict[str, Any] | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        条件に一致するレコードを複数取得
        
        Args:
            criteria: 検索条件（キー・値のペア）
            limit: 取得件数の上限
            offset: スキップする件数
            
        Returns:
            レコードのリスト
        """
        pass
    
    @abstractmethod
    def find_one(self, criteria: dict[str, Any]) -> dict[str, Any] | None:
        """
        条件に一致する最初のレコードを取得
        
        Args:
            criteria: 検索条件（キー・値のペア）
            
        Returns:
            レコード辞書、見つからない場合はNone
        """
        pass
    
    @abstractmethod
    def insert(self, data: dict[str, Any]) -> str:
        """
        レコードを挿入
        
        Args:
            data: 挿入するデータ
            
        Returns:
            生成されたレコードID
        """
        pass
    
    @abstractmethod
    def update(self, id: str, data: dict[str, Any]) -> bool:
        """
        レコードを更新
        
        Args:
            id: レコードID
            data: 更新するデータ
            
        Returns:
            更新成功時はTrue、失敗時はFalse
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        レコードを削除
        
        Args:
            id: レコードID
            
        Returns:
            削除成功時はTrue、失敗時はFalse
        """
        pass
    
    @abstractmethod
    def count(self, criteria: dict[str, Any] | None = None) -> int:
        """
        条件に一致するレコード数を取得
        
        Args:
            criteria: 検索条件（キー・値のペア）
            
        Returns:
            レコード数
        """
        pass
    
    @abstractmethod
    def exists(self, criteria: dict[str, Any]) -> bool:
        """
        条件に一致するレコードが存在するか確認
        
        Args:
            criteria: 検索条件（キー・値のペア）
            
        Returns:
            存在する場合はTrue、存在しない場合はFalse
        """
        pass
