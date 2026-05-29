"""認証サービス"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from ..models.user import User
from ..models.session import Session
from ..dal.user_dal import UserDAL
from ..dal.session_dal import SessionDAL
from ..core.security import hash_password, verify_password, create_access_token, verify_token
import uuid


class AuthService:
    """認証ビジネスロジック"""
    
    def __init__(self, user_dal: UserDAL, session_dal: SessionDAL):
        self.user_dal = user_dal
        self.session_dal = session_dal
    
    def authenticate(self, username: str, password: str) -> Tuple[User, str]:
        """ユーザー認証"""
        # ユーザー取得
        user_data = self.user_dal.find_by_username(username)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "ERR-SYS-AUTH-001", "message": "ユーザー名またはパスワードが正しくありません"}
            )
        
        user = User.from_dict(user_data)
        
        # パスワード検証
        if not user.validate_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "ERR-SYS-AUTH-001", "message": "ユーザー名またはパスワードが正しくありません"}
            )
        
        # JWT生成
        token = create_access_token(data={
            "sub": user.id,
            "username": user.username,
            "role": user.role
        })
        
        # 最終ログイン日時更新
        self.user_dal.update_last_login(user.id)
        
        # セッション作成
        session = self.create_session(user, token)
        
        return user, token
    
    def create_session(self, user: User, token: str) -> Session:
        """セッション作成"""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=24)
        
        session_data = {
            "sessionId": session_id,
            "userId": user.id,
            "token": token,
            "createdAt": now.isoformat() + "Z",
            "expiresAt": expires_at.isoformat() + "Z",
            "metadata": {}
        }
        
        self.session_dal.insert(session_data)
        return Session.from_dict(session_data)
    
    def logout(self, token: str) -> bool:
        """ログアウト"""
        session_data = self.session_dal.find_by_token(token)
        if not session_data:
            return False
        
        return self.session_dal.delete(session_data["sessionId"])
    
    def get_current_user(self, token: str) -> User:
        """現在のユーザーを取得"""
        # JWT検証
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "ERR-SYS-AUTH-002", "message": "認証トークンが無効です"}
            )
        
        # セッション存在確認
        session_data = self.session_dal.find_by_token(token)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "ERR-SYS-AUTH-005", "message": "セッションが存在しません"}
            )
        
        # ユーザー取得
        user_id = payload.get("sub")
        user_data = self.user_dal.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "ERR-SYS-USER-001", "message": "ユーザーが見つかりません"}
            )
        
        return User.from_dict(user_data)
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """パスワード変更"""
        # ユーザー取得
        user_data = self.user_dal.find_one({"id": user_id})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-USER-001", "message": "ユーザーが見つかりません"}
            )
        
        user = User.from_dict(user_data)
        
        # 現在のパスワード検証
        if not user.validate_password(current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ERR-SYS-AUTH-007", "message": "現在のパスワードが正しくありません"}
            )
        
        # 新しいパスワードの強度チェック
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ERR-SYS-AUTH-008", "message": "新しいパスワードは8文字以上である必要があります"}
            )
        
        # パスワードハッシュを更新
        new_hash = hash_password(new_password)
        return self.user_dal.update(user_id, {
            "passwordHash": new_hash,
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        })
