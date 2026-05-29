"""ユーザーサービス"""
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException, status
import uuid
from ..models.user import User, UserCreate, UserUpdate
from ..dal.user_dal import UserDAL
from ..core.security import hash_password


class UserService:
    """ユーザー管理ビジネスロジック"""
    
    def __init__(self, dal: UserDAL):
        self.dal = dal
    
    def list_users(self, role: Optional[str] = None, limit: int = 100, offset: int = 0) -> Tuple[list[User], int]:
        """ユーザー一覧を取得"""
        criteria = {}
        if role:
            criteria["role"] = role
        
        user_data_list = self.dal.find(criteria, limit=limit, offset=offset)
        users = [User.from_dict(data) for data in user_data_list]
        total = self.dal.count(criteria)
        
        return users, total
    
    def get_user(self, user_id: str) -> User:
        """ユーザー詳細を取得"""
        user_data = self.dal.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-USER-001", "message": "ユーザーが見つかりません"}
            )
        
        return User.from_dict(user_data)
    
    def create_user(self, user_create: UserCreate) -> User:
        """ユーザーを作成"""
        # バリデーション
        is_valid, error_msg = self.validate_user_data(user_create.model_dump())
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": error_msg}
            )
        
        # ユーザー名重複チェック
        if self.dal.find_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "ERR-SYS-USER-002", "message": "ユーザー名が既に存在します"}
            )
        
        # メールアドレス重複チェック
        if self.dal.find_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "ERR-SYS-USER-003", "message": "メールアドレスが既に存在します"}
            )
        
        # パスワードハッシュ化
        password_hash = hash_password(user_create.password)
        
        # ユーザーデータ作成
        now = datetime.utcnow()
        user_data = {
            "id": str(uuid.uuid4()),
            "username": user_create.username,
            "passwordHash": password_hash,
            "displayName": user_create.displayName,
            "role": user_create.role,
            "email": user_create.email,
            "metadata": user_create.metadata,
            "createdAt": now.isoformat() + "Z",
            "updatedAt": now.isoformat() + "Z",
            "lastLogin": None
        }
        
        self.dal.insert(user_data)
        return User.from_dict(user_data)
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """ユーザーを更新"""
        # ユーザー存在確認
        user_data = self.dal.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-USER-001", "message": "ユーザーが見つかりません"}
            )
        
        # 更新データ作成
        update_data = user_update.model_dump(exclude_unset=True)
        
        # メールアドレス重複チェック
        if "email" in update_data:
            existing_user = self.dal.find_by_email(update_data["email"])
            if existing_user and existing_user["id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "ERR-SYS-USER-003", "message": "メールアドレスが既に存在します"}
                )
        
        update_data["updatedAt"] = datetime.utcnow().isoformat() + "Z"
        
        self.dal.update(user_id, update_data)
        
        # 更新後のデータを取得
        updated_data = self.dal.find_one({"id": user_id})
        return User.from_dict(updated_data)
    
    def delete_user(self, user_id: str, current_user_id: str) -> bool:
        """ユーザーを削除"""
        # 自己削除防止
        if user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ERR-SYS-USER-007", "message": "自分自身を削除することはできません"}
            )
        
        # ユーザー存在確認
        user_data = self.dal.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-USER-001", "message": "ユーザーが見つかりません"}
            )
        
        return self.dal.delete(user_id)
    
    def validate_user_data(self, data: dict) -> Tuple[bool, str]:
        """ユーザーデータをバリデーション"""
        # ユーザー名チェック
        username = data.get("username", "")
        if not (3 <= len(username) <= 50):
            return False, "ユーザー名は3文字以上50文字以内である必要があります"
        
        # 表示名チェック
        display_name = data.get("displayName", "")
        if not (1 <= len(display_name) <= 100):
            return False, "表示名は1文字以上100文字以内である必要があります"
        
        # ロールチェック
        role = data.get("role", "")
        if role not in ["admin", "user"]:
            return False, "ロールは admin または user である必要があります"
        
        return True, ""
