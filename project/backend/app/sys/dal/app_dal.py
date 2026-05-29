"""アプリDAL"""
from typing import Optional
from .json_dal import JsonDAL


class AppDAL(JsonDAL):
    """アプリ専用DAL"""
    
    collection_name = "apps"
    
    def find_enabled(self) -> list[dict]:
        """有効化されているアプリのみ取得"""
        return self.find({"enabled": True})
    
    def find_by_name(self, name: str) -> Optional[dict]:
        """アプリ名でアプリを検索"""
        return self.find_one({"name": name})
