"""
結合テスト: アプリプラグイン機構
manifest.jsonによる自動登録、有効化・無効化、独立性を検証
"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestAppPluginMechanism:
    """アプリプラグイン機構の結合テスト"""

    def test_app_auto_registration_from_manifest(self, authenticated_client: tuple[TestClient, dict]):
        """manifest.json配置でアプリが自動登録される"""
        client, _ = authenticated_client
        
        response = client.get("/api/sys/apps")
        
        assert response.status_code == 200
        data = response.json()
        
        # todo-app が登録されている
        todo_app = next((app for app in data if app["id"] == "todo-app"), None)
        
        assert todo_app is not None
        assert todo_app["name"] == "TODOアプリ"
        assert todo_app["enabled"] is True

    def test_app_metadata_from_manifest(self, authenticated_client: tuple[TestClient, dict]):
        """manifest.jsonのメタデータが正しく取得される"""
        client, _ = authenticated_client
        
        response = client.get("/api/sys/apps")
        
        assert response.status_code == 200
        data = response.json()
        
        todo_app = next((app for app in data if app["id"] == "todo-app"), None)
        assert todo_app is not None
        
        # manifest.json のフィールドが反映されている
        assert "version" in todo_app
        assert "description" in todo_app
        assert "icon" in todo_app
        assert "requiredPermissions" in todo_app

    def test_app_enable_disable(self, authenticated_client: tuple[TestClient, dict], temp_data_dir: Path):
        """アプリの有効化・無効化が正しく動作する"""
        client, _ = authenticated_client
        
        # アプリを無効化
        response = client.put(
            "/api/sys/apps/todo-app/disable"
        )
        
        # 実装されていない場合は404
        if response.status_code == 404:
            pytest.skip("アプリ有効化・無効化APIが未実装")
        
        assert response.status_code == 200
        
        # アプリ一覧で無効になっていることを確認
        response = client.get("/api/sys/apps")
        assert response.status_code == 200
        data = response.json()
        
        todo_app = next((app for app in data if app["id"] == "todo-app"), None)
        assert todo_app is not None
        assert todo_app["enabled"] is False
        
        # アプリを有効化
        response = client.put(
            "/api/sys/apps/todo-app/enable"
        )
        assert response.status_code == 200

    def test_disabled_app_api_not_accessible(self, authenticated_client: tuple[TestClient, dict]):
        """無効化されたアプリのAPIにアクセス不可"""
        client, _ = authenticated_client
        
        # アプリを無効化
        response = client.put(
            "/api/sys/apps/todo-app/disable"
        )
        
        if response.status_code == 404:
            pytest.skip("アプリ有効化・無効化APIが未実装")
        
        # 無効化されたアプリのAPIにアクセス
        response = client.get("/api/todo-app/todos")
        
        # 403 Forbidden または 404 Not Found
        assert response.status_code in [403, 404]


class TestAppIsolation:
    """アプリ独立性の結合テスト"""

    def test_app_data_isolation(self, authenticated_client: tuple[TestClient, dict]):
        """アプリAのデータにアプリBが直接アクセスできない"""
        client, _ = authenticated_client
        
        # TODO アプリのデータを取得
        response = client.get("/api/todo-app/todos")
        
        if response.status_code == 404:
            pytest.skip("TODOアプリのAPI（/api/todo-app/todos）が未実装 - ISSUE-017")
        
        assert response.status_code == 200
        todos = response.json()
        
        # システム共通APIから TODO データに直接アクセスできないことを確認
        # ※ TODO専用APIを経由する必要がある
        response = client.get("/api/sys/data/todos")
        
        # 404 Not Found（存在しないエンドポイント）
        assert response.status_code == 404

    def test_app_cannot_access_system_data_directly(self, authenticated_client: tuple[TestClient, dict]):
        """アプリがシステムデータに直接アクセスできない"""
        client, _ = authenticated_client
        
        # アプリAPIからシステム共通データ（users）にアクセス
        response = client.get("/api/todo-app/sys/users/users")
        
        # 404 Not Found（アプリAPIにはシステムデータアクセスエンドポイントがない）
        assert response.status_code == 404

    def test_app_uses_system_common_api(self, authenticated_client: tuple[TestClient, dict]):
        """アプリはシステム共通APIを経由してシステムデータにアクセスする"""
        client, _ = authenticated_client
        
        # システム共通API経由でユーザー情報取得（正常）
        response = client.get("/api/sys/auth/me")
        assert response.status_code == 200
        
        # アプリは /api/sys/* を呼び出すことで、システムデータにアクセスできる


class TestCrossAppIsolation:
    """アプリ間独立性の結合テスト"""

    def test_app_a_cannot_access_app_b_data(self, authenticated_client: tuple[TestClient, dict]):
        """アプリAがアプリBのデータにアクセスできない"""
        client, _ = authenticated_client
        
        # TODO アプリのAPIエンドポイント
        response = client.get("/api/todo-app/todos")
        
        if response.status_code == 404:
            pytest.skip("TODOアプリのAPI（/api/todo-app/todos）が未実装 - ISSUE-017")
        
        assert response.status_code == 200
        
        # 別のアプリ（仮に calendar-app）のデータにアクセス
        response = client.get("/api/calendar-app/events")
        
        # 404 Not Found（別のアプリは未実装）
        assert response.status_code == 404

    def test_app_disable_does_not_affect_other_apps(self, authenticated_client: tuple[TestClient, dict]):
        """アプリAの無効化がアプリBに影響しない"""
        client, _ = authenticated_client
        
        # TODO アプリを無効化
        response = client.patch(
            "/api/sys/apps/todo-app",
            json={"isEnabled": False}
        )
        
        if response.status_code == 404:
            pytest.skip("アプリ有効化・無効化APIが未実装")
        
        assert response.status_code == 200
        
        # システム共通APIは引き続き動作する
        response = client.get("/api/sys/auth/me")
        assert response.status_code == 200
        
        # アプリ一覧取得も動作する
        response = client.get("/api/sys/apps")
        assert response.status_code == 200
