"""
JWT認証サービス

このモジュールはJWT（JSON Web Token）の生成・検証を担当します。
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Any


class JWTService:
    """
    JWTトークンの生成・検証を担当するサービスクラス
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        expiration_hours: int = 24
    ):
        """
        JWTServiceの初期化
        
        Args:
            secret_key: JWT署名用の秘密鍵
            algorithm: 署名アルゴリズム（デフォルト: HS256）
            expiration_hours: トークン有効期限（時間単位、デフォルト: 24時間）
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
    
    def create_token(self, user_data: dict[str, Any]) -> str:
        """
        JWTトークンを生成
        
        Args:
            user_data: ユーザー情報（id, username, role など）
            
        Returns:
            生成されたJWTトークン文字列
        """
        # トークンペイロード作成
        payload = {
            "sub": user_data.get("id"),
            "username": user_data.get("username"),
            "role": user_data.get("role"),
            "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
            "iat": datetime.utcnow()
        }
        
        # トークン生成
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> dict[str, Any] | None:
        """
        JWTトークンを検証し、ペイロードを返す
        
        Args:
            token: 検証するJWTトークン
            
        Returns:
            検証成功時はペイロード辞書、失敗時はNone
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None
    
    def decode_token(self, token: str) -> dict[str, Any]:
        """
        JWTトークンをデコード（検証含む）
        
        Args:
            token: デコードするJWTトークン
            
        Returns:
            ペイロード辞書
            
        Raises:
            JWTError: デコード失敗時
        """
        payload = jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]
        )
        return payload
    
    def refresh_token(self, token: str) -> str | None:
        """
        既存のトークンをリフレッシュ
        
        Args:
            token: 既存のJWTトークン
            
        Returns:
            新しいJWTトークン、検証失敗時はNone
        """
        payload = self.verify_token(token)
        if not payload:
            return None
        
        # 新しいトークンを生成（expとiatを更新）
        user_data = {
            "id": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role")
        }
        
        return self.create_token(user_data)
