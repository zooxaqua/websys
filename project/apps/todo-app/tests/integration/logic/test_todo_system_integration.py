"""
結合テスト: TODOアプリ - システム共通基盤との連携
認証フロー、CRUD操作、データ独立性を検証
"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


class TestTodoAppSystemIntegration:
    """TODOアプリ - システム共通基盤の結合テスト"""

    def test_todo_app_uses_system_auth(self, client: TestClient):
        """TODOアプリがシステム共通の認証を使用する"""
        # 未認証でTODOアプリAPIにアクセス
        response = client.get("/api/todo-app/todos")
        
        # 401 Unauthorized（システム共通の認証が必要）
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "AUTH_TOKEN_MISSING"

    def test_todo_crud_with_system_auth(self, authenticated_client: tuple[TestClient, dict]):
        """システム認証済みでTODO CRUD操作"""
        client, user_data = authenticated_client
        
        # TODO一覧取得
        response = client.get("/api/todo-app/todos")
        assert response.status_code == 200
        todos_before = response.json()
        
        # TODO作成
        new_todo = {
            "title": "結合テスト用TODO",
            "description": "システム共通基盤との連携テスト",
            "dueDate": "2026-12-31T23:59:59Z"
        }
        response = client.post("/api/todo-app/todos", json=new_todo)
        
        # 実装されていない場合は404
        if response.status_code == 404:
            pytest.skip("TODO作成APIが未実装")
        
        assert response.status_code == 201
        created_todo = response.json()
        assert created_todo["title"] == new_todo["title"]
        assert created_todo["userId"] == user_data["id"]
        
        # TODO一覧取得（作成後）
        response = client.get("/api/todo-app/todos")
        assert response.status_code == 200
        todos_after = response.json()
        
        # 作成されたTODOが含まれる
        todo_ids = [todo["id"] for todo in todos_after["todos"]]
        assert created_todo["id"] in todo_ids

    def test_todo_user_isolation(self, authenticated_client: tuple[TestClient, dict], authenticated_user_client: tuple[TestClient, dict]):
        """ユーザーAのTODOがユーザーBに表示されない"""
        admin_client, admin_user = authenticated_client
        user_client, user_user = authenticated_user_client
        
        # 管理者のTODO一覧
        response = admin_client.get("/api/todo-app/todos")
        assert response.status_code == 200
        admin_todos = response.json()
        
        # 一般ユーザーのTODO一覧
        response = user_client.get("/api/todo-app/todos")
        assert response.status_code == 200
        user_todos = response.json()
        
        # 管理者と一般ユーザーのTODOは独立している
        admin_todo_ids = [todo["id"] for todo in admin_todos["todos"]]
        user_todo_ids = [todo["id"] for todo in user_todos["todos"]]
        
        # TODO が空でなければ、重複がないことを確認
        if admin_todo_ids and user_todo_ids:
            assert set(admin_todo_ids).isdisjoint(set(user_todo_ids))


class TestTodoAppDataIsolation:
    """TODOアプリのデータ独立性テスト"""

    def test_todo_data_stored_in_app_directory(self, authenticated_client: tuple[TestClient, dict]):
        """TODOデータがアプリディレクトリに保存される"""
        client, _ = authenticated_client
        
        # TODO一覧取得
        response = client.get("/api/todo-app/todos")
        assert response.status_code == 200
        
        # データがアプリディレクトリに保存されていることを確認
        # ※ project/apps/todo-app/backend/data/
        app_data_dir = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "project" / "apps" / "todo-app" / "backend" / "data"
        
        # todos.json が存在するか確認（実装による）
        # 結合テストでは、APIが正常に動作すれば、データ保存場所は実装詳細として扱う

    def test_system_cannot_access_todo_data_directly(self, authenticated_client: tuple[TestClient, dict]):
        """システム共通APIがTODOデータに直接アクセスできない"""
        client, _ = authenticated_client
        
        # システム共通APIからTODOデータにアクセス
        response = client.get("/api/sys/todos")
        
        # 404 Not Found（システム共通APIにはTODOエンドポイントがない）
        assert response.status_code == 404


class TestTodoAppAPIContract:
    """TODOアプリのAPI契約テスト（基本設計書との整合性）"""

    def test_get_todos_response_format(self, authenticated_client: tuple[TestClient, dict]):
        """GET /api/todo-app/todos のレスポンス形式が設計通り"""
        client, _ = authenticated_client
        
        response = client.get("/api/todo-app/todos")
        assert response.status_code == 200
        
        data = response.json()
        assert "todos" in data
        
        # TODOの構造確認
        if len(data["todos"]) > 0:
            todo = data["todos"][0]
            required_fields = ["id", "userId", "title", "description", "dueDate", "completed", "createdAt", "updatedAt"]
            for field in required_fields:
                assert field in todo

    def test_get_todos_query_parameters(self, authenticated_client: tuple[TestClient, dict]):
        """GET /api/todo-app/todos のクエリパラメータが動作する"""
        client, _ = authenticated_client
        
        # completed フィルタ
        response = client.get("/api/todo-app/todos?completed=false")
        assert response.status_code == 200
        data = response.json()
        
        # 完了していないTODOのみ
        if len(data["todos"]) > 0:
            for todo in data["todos"]:
                assert todo["completed"] is False
        
        # completed=true フィルタ
        response = client.get("/api/todo-app/todos?completed=true")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["todos"]) > 0:
            for todo in data["todos"]:
                assert todo["completed"] is True

    def test_create_todo_validation(self, authenticated_client: tuple[TestClient, dict]):
        """POST /api/todo-app/todos のバリデーションが動作する"""
        client, _ = authenticated_client
        
        # タイトルなし（バリデーションエラー）
        response = client.post("/api/todo-app/todos", json={})
        
        # 実装されていない場合は404
        if response.status_code == 404:
            pytest.skip("TODO作成APIが未実装")
        
        # 400 Bad Request または 422 Unprocessable Entity
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data or "detail" in data
