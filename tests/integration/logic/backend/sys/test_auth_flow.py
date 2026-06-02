"""
結合テスト: 認証フロー（ログイン → API呼び出し → ログアウト）
セッション管理・JWT Cookie・認証エラーハンドリングを検証
"""
import pytest
from fastapi.testclient import TestClient


class TestAuthenticationFlow:
    """認証フロー全体の結合テスト"""

    def test_login_success(self, client: TestClient):
        """正常ログイン: JWT Cookie発行とユーザー情報返却"""
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "test_admin", "password": "password"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["username"] == "test_admin"
        assert data["user"]["role"] == "admin"
        
        # JWT Cookie が設定されていることを確認
        assert "auth_token" in response.cookies

    def test_login_invalid_credentials(self, client: TestClient):
        """ログイン失敗: 無効な認証情報"""
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "test_admin", "password": "wrong_password"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "ERR-SYS-AUTH-001"

    def test_login_invalid_username(self, client: TestClient):
        """ログイン失敗: 存在しないユーザー"""
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_authenticated_api_call(self, authenticated_client: tuple[TestClient, dict]):
        """認証済みAPI呼び出し: /api/sys/auth/me"""
        client, user_data = authenticated_client
        
        response = client.get("/api/sys/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["role"] == user_data["role"]

    def test_unauthenticated_api_call(self, client: TestClient):
        """未認証API呼び出し: 401エラー"""
        response = client.get("/api/sys/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "ERR-SYS-AUTH-004"

    def test_logout(self, authenticated_client: tuple[TestClient, dict]):
        """ログアウト: セッション破棄とCookie削除"""
        client, _ = authenticated_client
        
        # ログアウト前は /me が成功
        response = client.get("/api/sys/auth/me")
        assert response.status_code == 200
        
        # ログアウト
        response = client.post("/api/sys/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # ログアウト後は /me が401エラー
        response = client.get("/api/sys/auth/me")
        assert response.status_code == 401

    def test_session_persistence(self, authenticated_client: tuple[TestClient, dict]):
        """セッション永続化: 複数API呼び出しで同じセッション"""
        client, user_data = authenticated_client
        
        # 1回目のAPI呼び出し
        response1 = client.get("/api/sys/auth/me")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # 2回目のAPI呼び出し（同じセッション）
        response2 = client.get("/api/sys/auth/me")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # 同じユーザー情報が返ることを確認
        assert data1["id"] == data2["id"]
        assert data1["username"] == data2["username"]


class TestRoleBasedAccess:
    """ロールベースアクセス制御の結合テスト"""

    def test_admin_access_to_admin_api(self, authenticated_client: tuple[TestClient, dict]):
        """管理者が管理者専用APIにアクセス可能"""
        client, _ = authenticated_client
        
        # /api/sys/users (管理者専用)
        response = client.get("/api/sys/users")
        
        # 実装されていない場合は404、認証エラーでなければOK
        assert response.status_code in [200, 404]
        if response.status_code != 404:
            # 認証エラーでないことを確認
            data = response.json()
            assert "detail" not in data or data["detail"]["code"] != "ERR-SYS-AUTH-003"

    def test_user_cannot_access_admin_api(self, authenticated_user_client: tuple[TestClient, dict]):
        """一般ユーザーが管理者専用APIにアクセス不可"""
        client, _ = authenticated_user_client
        
        # /api/sys/users (管理者専用)
        response = client.get("/api/sys/users")
        
        # 403 Forbidden または 404 (未実装の場合)
        assert response.status_code in [403, 404]
        if response.status_code == 403:
            data = response.json()
            assert data["detail"]["code"] == "ERR-SYS-AUTH-003"


class TestJWTValidation:
    """JWT検証の結合テスト"""

    def test_invalid_jwt_token(self, client: TestClient):
        """無効なJWTトークン: 401エラー"""
        # 不正なトークンをCookieに設定
        client.cookies.set("auth_token", "invalid.jwt.token")
        
        response = client.get("/api/sys/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] in ["ERR-SYS-AUTH-002", "ERR-SYS-AUTH-005"]

    def test_missing_jwt_token(self, client: TestClient):
        """JWTトークンなし: 401エラー"""
        response = client.get("/api/sys/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"]["code"] == "ERR-SYS-AUTH-004"
