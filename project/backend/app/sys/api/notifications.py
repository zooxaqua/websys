"""通知API"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from ..models.notification import NotificationCreate, NotificationResponse
from ..models.user import User
from ..services.notification_service import NotificationService
from ..core.dependencies import get_notification_service, get_current_user

router = APIRouter(tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """通知一覧を取得"""
    notifications = notification_service.get_user_notifications(
        current_user.id,
        unread_only=unread_only
    )
    return [NotificationResponse(**notif.model_dump()) for notif in notifications]


@router.post("", response_model=NotificationResponse, status_code=201)
def create_notification(
    notif_create: NotificationCreate,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """通知を作成（テスト用）"""
    notification = notification_service.create_notification(
        current_user.id,
        notif_create
    )
    return NotificationResponse(**notification.model_dump())


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """通知を既読にする"""
    notification_service.mark_as_read(notification_id, current_user.id)
    return {"success": True, "message": "通知を既読にしました"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """通知を削除"""
    notification_service.delete_notification(notification_id, current_user.id)
    return {"success": True, "message": "通知を削除しました"}


@router.get("/stream")
async def stream_notifications(
    current_user: User = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """SSEで通知をストリーミング"""
    return StreamingResponse(
        notification_service.stream_notifications(current_user.id),
        media_type="text/event-stream"
    )
