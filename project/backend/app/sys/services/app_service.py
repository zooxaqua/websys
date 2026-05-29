"""アプリサービス"""
import json
from pathlib import Path
from typing import Optional
from fastapi import HTTPException, status
from datetime import datetime
from ..models.app import App
from ..dal.app_dal import AppDAL


class AppService:
    """アプリ管理ビジネスロジック"""
    
    def __init__(self, dal: AppDAL):
        self.dal = dal
    
    def scan_apps(self, apps_dir: str = "./apps") -> list[App]:
        """アプリディレクトリをスキャンしてアプリを登録"""
        apps_path = Path(apps_dir)
        if not apps_path.exists():
            return []
        
        apps = []
        
        for app_dir in apps_path.iterdir():
            if not app_dir.is_dir():
                continue
            
            manifest_path = app_dir / "manifest.json"
            if not manifest_path.exists():
                continue
            
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                
                # バリデーション
                is_valid, error = self.validate_app_manifest(manifest)
                if not is_valid:
                    print(f"Invalid manifest for {app_dir.name}: {error}")
                    continue
                
                # アプリデータ作成
                app_id = manifest["name"]
                existing_app = self.dal.find_one({"id": app_id})
                
                app_data = {
                    "id": app_id,
                    "name": manifest["displayName"],
                    "version": manifest["version"],
                    "description": manifest.get("description", ""),
                    "icon": f"/apps/{app_id}/{manifest.get('icon', 'icon.png')}",
                    "entryPoint": manifest["entryPoint"],
                    "apiPrefix": manifest["apiPrefix"],
                    "enabled": existing_app["enabled"] if existing_app else True,
                    "author": manifest.get("author", "Unknown"),
                    "requiredPermissions": manifest.get("requiredPermissions", []),
                    "dependencies": manifest.get("dependencies", []),
                    "manifest": manifest,
                    "lastUpdated": datetime.utcnow().isoformat() + "Z"
                }
                
                if existing_app:
                    self.dal.update(app_id, app_data)
                else:
                    self.dal.insert(app_data)
                
                apps.append(App.from_dict(app_data))
            
            except (json.JSONDecodeError, IOError) as e:
                print(f"Failed to load manifest for {app_dir.name}: {e}")
                continue
        
        return apps
    
    def list_apps(self, enabled: Optional[bool] = None) -> list[App]:
        """アプリ一覧を取得"""
        if enabled is not None:
            app_data_list = self.dal.find({"enabled": enabled})
        else:
            app_data_list = self.dal.find({})
        
        return [App.from_dict(data) for data in app_data_list]
    
    def get_app(self, app_id: str) -> App:
        """アプリ詳細を取得"""
        app_data = self.dal.find_one({"id": app_id})
        if not app_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-APPS-001", "message": "アプリが見つかりません"}
            )
        
        return App.from_dict(app_data)
    
    def enable_app(self, app_id: str) -> bool:
        """アプリを有効化"""
        app_data = self.dal.find_one({"id": app_id})
        if not app_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-APPS-001", "message": "アプリが見つかりません"}
            )
        
        if app_data["enabled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ERR-SYS-APPS-002", "message": "アプリは既に有効化されています"}
            )
        
        return self.dal.update(app_id, {
            "enabled": True,
            "lastUpdated": datetime.utcnow().isoformat() + "Z"
        })
    
    def disable_app(self, app_id: str) -> bool:
        """アプリを無効化"""
        app_data = self.dal.find_one({"id": app_id})
        if not app_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "ERR-SYS-APPS-001", "message": "アプリが見つかりません"}
            )
        
        if not app_data["enabled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "ERR-SYS-APPS-003", "message": "アプリは既に無効化されています"}
            )
        
        return self.dal.update(app_id, {
            "enabled": False,
            "lastUpdated": datetime.utcnow().isoformat() + "Z"
        })
    
    def validate_app_manifest(self, manifest: dict) -> tuple[bool, str]:
        """マニフェストの妥当性を検証"""
        required_fields = ["name", "version", "displayName", "entryPoint", "apiPrefix"]
        
        for field in required_fields:
            if field not in manifest:
                return False, f"必須フィールド '{field}' が不足しています"
        
        return True, ""
    
    def reload_app(self, app_id: str) -> App:
        """アプリをリロード"""
        # 再スキャン
        self.scan_apps()
        
        # 更新後のデータを取得
        return self.get_app(app_id)
