"""
結合テスト用 pytest設定ファイル（システム共通基盤）
テストクライアント・フィクスチャ・モックの設定
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Generator

import pytest
import sys

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

# プロジェクトルートをsys.pathに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "project" / "backend"))


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """テストデータディレクトリのパス"""
    return Path(__file__).parent.parent.parent.parent / "inputs" / "fixtures"


@pytest.fixture(scope="function")
def temp_data_dir(test_data_dir: Path) -> Generator[Path, None, None]:
    """
    テスト用の一時データディレクトリ
    各テストごとにクリーンな状態を提供
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # テストフィクスチャをコピー
        users_src = test_data_dir / "test_users.json"
        apps_src = test_data_dir / "test_apps.json"
        
        if users_src.exists():
            shutil.copy(users_src, tmp_path / "users.json")
        if apps_src.exists():
            shutil.copy(apps_src, tmp_path / "apps.json")
        
        # sessions ディレクトリ作成
        (tmp_path / "sessions").mkdir(exist_ok=True)
        
        # notifications.json 初期化
        (tmp_path / "notifications.json").write_text("[]", encoding="utf-8")
        
        # config.json 初期化
        config_data = {
            "systemName": "Webシステム開発プラットフォーム（テスト環境）",
            "version": "1.0.0-test",
            "environment": "test",
            "features": {
                "enableRegistration": False,
                "enableNotifications": True
            }
        }
        (tmp_path / "config.json").write_text(json.dumps(config_data, ensure_ascii=False, indent=2), encoding="utf-8")
        
        # 環境変数でデータディレクトリを設定
        original_data_path = os.environ.get("DATA_DIR")
        os.environ["DATA_DIR"] = str(tmp_path)
        
        yield tmp_path
        
        # 元に戻す
        if original_data_path:
            os.environ["DATA_DIR"] = original_data_path
        else:
            os.environ.pop("DATA_DIR", None)


@pytest.fixture(scope="function")
def client(temp_data_dir: Path) -> "TestClient":
    """
    FastAPI TestClient
    各テストごとに独立したデータディレクトリで実行
    """
    # temp_data_dir フィクスチャで既に環境変数は設定済み
    # ここでアプリをインポート
    from fastapi.testclient import TestClient
    import importlib
    
    # configモジュールをリロードして環境変数の変更を反映
    import app.sys.core.config as config_module
    importlib.reload(config_module)
    
    # dependenciesモジュールもリロード（settingsへの参照を更新）
    import app.sys.core.dependencies as dependencies_module
    importlib.reload(dependencies_module)
    
    # アプリをインポート（リロードされたモジュールを使用）
    from app.sys.main import app
    
    return TestClient(app)


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient) -> tuple[TestClient, dict]:
    """
    認証済みTestClient
    ログイン済みの状態でテストを実行できる
    
    Returns:
        tuple[TestClient, dict]: (クライアント, ユーザー情報)
    """
    # ログイン
    response = client.post(
        "/api/sys/auth/login",
        json={"username": "test_admin", "password": "password"}
    )
    assert response.status_code == 200
    user_data = response.json()["user"]
    
    return client, user_data


@pytest.fixture(scope="function")
def authenticated_user_client(client: TestClient) -> tuple[TestClient, dict]:
    """
    一般ユーザーとして認証済みのTestClient
    
    Returns:
        tuple[TestClient, dict]: (クライアント, ユーザー情報)
    """
    # ログイン
    response = client.post(
        "/api/sys/auth/login",
        json={"username": "test_user", "password": "password"}
    )
    assert response.status_code == 200
    user_data = response.json()["user"]
    
    return client, user_data
