"""通知DAL"""
from typing import Optional
from .json_dal import JsonDAL


class NotificationDAL(JsonDAL):
    """通知専用DAL"""
    
    collection_name = "notifications"
    
    def find_by_user(self, user_id: str, unread_only: bool = False) -> list[dict]:
        """ユーザーの通知を取得"""
        criteria = {"userId": user_id}
        if unread_only:
            criteria["read"] = False
        
        return self.find(criteria, limit=100)
    
    def mark_read(self, notification_id: str) -> bool:
        """通知を既読にする"""
        return self.update(notification_id, {"read": True})
    
    def delete_expired(self) -> int:
        """期限切れ通知を削除"""
        from datetime import datetime
        
        all_data = self._load_data()
        deleted_count = 0
        
        for notif_id, notif in list(all_data.items()):
            expires_at = notif.get("expiresAt")
            if expires_at:
                if datetime.fromisoformat(expires_at.replace("Z", "+00:00")) < datetime.utcnow():
                    self.delete(notif_id)
                    deleted_count += 1
        
        return deleted_count
