"""ユーザーDAL"""
from datetime import datetime, timezone
from typing import Optional
from .json_dal import JsonDAL


class UserDAL(JsonDAL):
    """ユーザー専用DAL"""
    
    collection_name = "users"
    
    def find_by_username(self, username: str) -> Optional[dict]:
        """ユーザー名でユーザーを検索"""
        return self.find_one({"username": username})
    
    def find_by_email(self, email: str) -> Optional[dict]:
        """メールアドレスでユーザーを検索"""
        return self.find_one({"email": email})
    
    def update_last_login(self, user_id: str) -> bool:
        """最終ログイン日時を更新"""
        return self.update(user_id, {
            "lastLogin": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "updatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        })
