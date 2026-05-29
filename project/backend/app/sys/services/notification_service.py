"""通知サービス"""
from datetime import datetime
from typing import Optional, AsyncGenerator
from fastapi import HTTPException, status
import uuid
from ..models.notification import Notification, NotificationCreate
from ..dal.notification_dal import NotificationDAL


class NotificationService:
    """通知ビジネスロジック"""
    
    def __init__(self, dal: NotificationDAL):
        self.dal = dal
        self.active_connections: dict[str, list] = {}
    
    def create_notification(
        self,
        user_id: str,
        notif_create: NotificationCreate
    ) -> Notification:
        """通知を作成"""
        now = datetime.utcnow()
        
        notif_data = {
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "type": notif_create.type,
            "title": notif_create.title,
            "message": notif_create.message,
            "metadata": notif_create.metadata,
            "read": False,
            "createdAt": now.isoformat() + "Z",
            "expiresAt": notif_create.expiresAt.isoformat() + "Z" if notif_create.expiresAt else None
        }
        
        self.dal.insert(notif_data)
        return Notification.from_dict(notif_data)
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False) -> list[Notification]:
        """ユーザーの通知を取得"""
        notif_data_list = self.dal.find_by_user(user_id, unread_only=unread_only)
        return [Notification.from_dict(data) for data in notif_data_list]
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """通知を既読にする"""
        notif_data = self.dal.find_one({"id": notification_id})
        if not notif_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-NOTF-001", "message": "通知が見つかりません"}
            )
        
        # 権限チェック
        if notif_data["userId"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ERR-SYS-NOTF-002", "message": "この通知にアクセスする権限がありません"}
            )
        
        return self.dal.mark_read(notification_id)
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """通知を削除"""
        notif_data = self.dal.find_one({"id": notification_id})
        if not notif_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-NOTF-001", "message": "通知が見つかりません"}
            )
        
        # 権限チェック
        if notif_data["userId"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "ERR-SYS-NOTF-002", "message": "この通知にアクセスする権限がありません"}
            )
        
        return self.dal.delete(notification_id)
    
    async def stream_notifications(self, user_id: str) -> AsyncGenerator[str, None]:
        """SSEで通知をストリーミング"""
        # 簡易実装（実際にはRedis等を使用）
        import asyncio
        
        while True:
            # 未読通知を取得
            notifications = self.get_user_notifications(user_id, unread_only=True)
            
            for notif in notifications:
                yield f"data: {notif.model_dump_json()}\n\n"
            
            # 5秒待機
            await asyncio.sleep(5)
    
    def cleanup_expired(self) -> int:
        """期限切れ通知を削除"""
        return self.dal.delete_expired()
