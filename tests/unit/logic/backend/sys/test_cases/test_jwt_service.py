"""
単体テスト: JWTService

テスト対象: project/backend/app/sys/services/jwt_service.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.services.jwt_service import JWTService


class TestJWTService:
    """JWTService のテストクラス"""
    
    @pytest.fixture
    def jwt_service(self):
        """JWTService インスタンス"""
        return JWTService(
            secret_key="test_secret_key",
            algorithm="HS256",
            expiration_hours=24
        )
    
    @pytest.fixture
    def valid_user_data(self):
        """有効なユーザーデータ"""
        return {
            "id": "user-001",
            "username": "testuser",
            "role": "user"
        }
    
    # TC-JWT-001: 正常系 - トークン生成成功
    def test_create_token_success(self, jwt_service, valid_user_data):
        """トークン生成成功"""
        token = jwt_service.create_token(valid_user_data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # トークンをデコードして内容確認
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert payload["sub"] == "user-001"
        assert payload["username"] == "testuser"
        assert payload["role"] == "user"
    
    # TC-JWT-002: 正常系 - トークン検証成功
    def test_verify_token_success(self, jwt_service, valid_user_data):
        """トークン検証成功"""
        token = jwt_service.create_token(valid_user_data)
        
        payload = jwt_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user-001"
        assert payload["username"] == "testuser"
    
    # TC-JWT-003: 異常系 - 無効なトークン
    def test_verify_token_invalid(self, jwt_service):
        """無効なトークン"""
        result = jwt_service.verify_token("invalid.token.string")
        
        assert result is None
    
    # TC-JWT-004: 異常系 - 期限切れトークン
    def test_verify_token_expired(self, jwt_service, valid_user_data):
        """期限切れトークン"""
        # 過去の時刻でトークン作成
        past_time = datetime.now(timezone.utc) - timedelta(hours=25)
        payload = {
            "sub": valid_user_data["id"],
            "username": valid_user_data["username"],
            "role": valid_user_data["role"],
            "exp": past_time,
            "iat": past_time
        }
        expired_token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        result = jwt_service.verify_token(expired_token)
        
        assert result is None
    
    # TC-JWT-005: 異常系 - 署名が不正
    def test_verify_token_wrong_signature(self, jwt_service, valid_user_data):
        """署名が不正"""
        # 異なる秘密鍵でトークン作成
        wrong_service = JWTService(secret_key="wrong_secret", algorithm="HS256")
        token = wrong_service.create_token(valid_user_data)
        
        result = jwt_service.verify_token(token)
        
        assert result is None
    
    # TC-JWT-006: 正常系 - トークンデコード成功
    def test_decode_token_success(self, jwt_service, valid_user_data):
        """トークンデコード成功"""
        token = jwt_service.create_token(valid_user_data)
        
        payload = jwt_service.decode_token(token)
        
        assert payload["sub"] == "user-001"
        assert payload["username"] == "testuser"
    
    # TC-JWT-007: 異常系 - デコード失敗
    def test_decode_token_failure(self, jwt_service):
        """デコード失敗"""
        with pytest.raises(JWTError):
            jwt_service.decode_token("invalid.token.string")
    
    # TC-JWT-008: 正常系 - トークンリフレッシュ成功
    def test_refresh_token_success(self, jwt_service, valid_user_data):
        """トークンリフレッシュ成功"""
        old_token = jwt_service.create_token(valid_user_data)
        
        new_token = jwt_service.refresh_token(old_token)
        
        assert new_token is not None
        # 新しいトークンが有効か確認（同秒内生成の場合は同一トークンになりうる）
        payload = jwt_service.verify_token(new_token)
        assert payload is not None
        assert payload["sub"] == "user-001"
    
    # TC-JWT-009: 異常系 - リフレッシュ失敗（無効なトークン）
    def test_refresh_token_invalid(self, jwt_service):
        """リフレッシュ失敗（無効なトークン）"""
        result = jwt_service.refresh_token("invalid.token.string")
        
        assert result is None
    
    # TC-JWT-010: 境界値 - 有効期限直前のトークン
    def test_verify_token_about_to_expire(self, jwt_service, valid_user_data):
        """有効期限直前のトークン"""
        # 1秒後に期限切れのトークン
        near_future = datetime.now(timezone.utc) + timedelta(seconds=1)
        payload = {
            "sub": valid_user_data["id"],
            "username": valid_user_data["username"],
            "role": valid_user_data["role"],
            "exp": near_future,
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        result = jwt_service.verify_token(token)
        
        assert result is not None
        assert result["sub"] == "user-001"
    
    # TC-JWT-011: 境界値 - 有効期限切れ（1秒前）
    def test_verify_token_exactly_expired(self, jwt_service, valid_user_data):
        """有効期限切れ（1秒前を期限に設定）"""
        # 1秒前を期限に設定して確実に期限切れ
        now = datetime.now(timezone.utc)
        payload = {
            "sub": valid_user_data["id"],
            "username": valid_user_data["username"],
            "role": valid_user_data["role"],
            "exp": now - timedelta(seconds=1),
            "iat": now - timedelta(seconds=2)
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        result = jwt_service.verify_token(token)
        
        # 期限切れのトークンはNoneを返す
        assert result is None
    
    # TC-JWT-012: 正常系 - カスタム有効期限（1時間）
    def test_create_token_custom_expiration(self):
        """カスタム有効期限（1時間）"""
        short_expiry_service = JWTService(
            secret_key="test_secret_key",
            algorithm="HS256",
            expiration_hours=1
        )
        user_data = {"id": "user-001", "username": "testuser", "role": "user"}
        
        token = short_expiry_service.create_token(user_data)
        
        payload = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        diff = (exp_time - iat_time).total_seconds()
        
        # 約1時間（3600秒）の差があるはず
        assert 3595 < diff < 3605


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
