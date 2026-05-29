"""
単体テスト: Core/Security
テスト対象: project/backend/app/sys/core/security.py
"""
import pytest
from datetime import datetime, timedelta
from project.backend.app.sys.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)


class TestHashPassword:
    """hash_password() のテスト"""
    
    def test_hash_password_normal(self):
        """
        TC-SECURITY-001: hash_password() - 正常系
        条件: 通常のパスワード
        期待: ハッシュ化された文字列を返す
        """
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_hash_password_empty(self):
        """
        TC-SECURITY-002: hash_password() - 空文字列
        条件: 空文字列
        期待: ハッシュ化された文字列を返す（bcryptは空文字列もハッシュ化可能）
        """
        password = ""
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) > 0
    
    def test_hash_password_long(self):
        """
        TC-SECURITY-003: hash_password() - 長い文字列
        条件: 100文字のパスワード
        期待: ハッシュ化された文字列を返す
        """
        password = "A" * 100
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) > 0
    
    def test_hash_password_uniqueness(self):
        """
        TC-SECURITY-004: hash_password() - ユニーク性
        条件: 同じパスワードを2回ハッシュ化
        期待: 異なるハッシュ値を返す（saltが異なる）
        """
        password = "SamePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2


class TestVerifyPassword:
    """verify_password() のテスト"""
    
    def test_verify_password_match(self):
        """
        TC-SECURITY-005: verify_password() - 一致
        条件: 正しいパスワードとハッシュ
        期待: True
        """
        password = "CorrectPassword"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_mismatch(self):
        """
        TC-SECURITY-006: verify_password() - 不一致
        条件: 誤ったパスワードとハッシュ
        期待: False
        """
        password = "CorrectPassword"
        wrong_password = "WrongPassword"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_plain(self):
        """
        TC-SECURITY-007: verify_password() - 空のプレーンパスワード
        条件: 空文字列と通常のハッシュ
        期待: False
        """
        password = "SomePassword"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False
    
    def test_verify_password_empty_both(self):
        """
        TC-SECURITY-008: verify_password() - 両方空
        条件: 空文字列のパスワードとそのハッシュ
        期待: True
        """
        password = ""
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_case_sensitive(self):
        """
        TC-SECURITY-009: verify_password() - 大文字小文字区別
        条件: 大文字小文字が異なるパスワード
        期待: False
        """
        password = "Password"
        hashed = hash_password(password)
        
        assert verify_password("password", hashed) is False


class TestCreateAccessToken:
    """create_access_token() のテスト"""
    
    def test_create_access_token_default_expiry(self):
        """
        TC-SECURITY-010: create_access_token() - デフォルト有効期限
        条件: expires_delta=None
        期待: JWTトークンを生成（デフォルト有効期限）
        """
        data = {"sub": "user-001", "username": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        assert token.count('.') == 2  # JWT format: header.payload.signature
    
    def test_create_access_token_custom_expiry(self):
        """
        TC-SECURITY-011: create_access_token() - カスタム有効期限
        条件: expires_delta=1時間
        期待: JWTトークンを生成（カスタム有効期限）
        """
        data = {"sub": "user-002", "username": "testuser2"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_minimal_data(self):
        """
        TC-SECURITY-012: create_access_token() - 最小データ
        条件: 必須フィールドのみ
        期待: JWTトークンを生成
        """
        data = {"sub": "user-003"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_access_token_large_data(self):
        """
        TC-SECURITY-013: create_access_token() - 大きなデータ
        条件: 多数のフィールド
        期待: JWTトークンを生成
        """
        data = {
            "sub": "user-004",
            "username": "testuser",
            "email": "test@example.com",
            "role": "admin",
            "extra1": "data1",
            "extra2": "data2"
        }
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_create_access_token_zero_expiry(self):
        """
        TC-SECURITY-014: create_access_token() - 即座に期限切れ
        条件: expires_delta=0秒
        期待: JWTトークンを生成（即座に期限切れ）
        """
        data = {"sub": "user-005"}
        token = create_access_token(data, expires_delta=timedelta(seconds=0))
        
        assert token is not None
        # このトークンは即座に期限切れになるが、生成自体は成功


class TestVerifyToken:
    """verify_token() のテスト"""
    
    def test_verify_token_valid(self):
        """
        TC-SECURITY-015: verify_token() - 有効なトークン
        条件: 有効なJWTトークン
        期待: ペイロードを返す
        """
        data = {"sub": "user-001", "username": "testuser"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user-001"
        assert payload["username"] == "testuser"
        assert "exp" in payload
    
    def test_verify_token_invalid_format(self):
        """
        TC-SECURITY-016: verify_token() - 無効なフォーマット
        条件: 不正なトークン文字列
        期待: None
        """
        invalid_token = "invalid.token.string"
        
        payload = verify_token(invalid_token)
        
        assert payload is None
    
    def test_verify_token_malformed(self):
        """
        TC-SECURITY-017: verify_token() - 不正な形式
        条件: 完全に不正な文字列
        期待: None
        """
        malformed_token = "notajwt"
        
        payload = verify_token(malformed_token)
        
        assert payload is None
    
    def test_verify_token_expired(self):
        """
        TC-SECURITY-018: verify_token() - 期限切れトークン
        条件: 期限切れのJWTトークン
        期待: None
        """
        data = {"sub": "user-002", "username": "testuser"}
        # 即座に期限切れになるトークンを生成
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        payload = verify_token(token)
        
        assert payload is None
    
    def test_verify_token_empty(self):
        """
        TC-SECURITY-019: verify_token() - 空文字列
        条件: 空のトークン
        期待: None
        """
        payload = verify_token("")
        
        assert payload is None
    
    def test_verify_token_roundtrip(self):
        """
        TC-SECURITY-020: verify_token() - ラウンドトリップ
        条件: トークン生成→検証のフルサイクル
        期待: 元のデータが取得できる
        """
        original_data = {
            "sub": "user-003",
            "username": "roundtrip_user",
            "role": "user"
        }
        token = create_access_token(original_data, expires_delta=timedelta(hours=1))
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == original_data["sub"]
        assert payload["username"] == original_data["username"]
        assert payload["role"] == original_data["role"]
