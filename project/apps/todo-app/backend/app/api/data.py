"""アプリデータAPI"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from pydantic import BaseModel
import sys
from pathlib import Path
import json

# システム共通基盤のモデルをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "backend"))

from app.sys.models.user import User
from app.sys.core.dependencies import get_current_user

router = APIRouter()


class DataItem(BaseModel):
    """データアイテム"""
    key: str
    value: Any


class DataResponse(BaseModel):
    """データレスポンス"""
    data: dict[str, Any]


# アプリ固有データの保存先
DATA_FILE = Path(__file__).parent.parent.parent / "data" / "app_data.json"


def load_app_data() -> dict[str, Any]:
    """アプリデータを読み込み"""
    if not DATA_FILE.exists():
        return {}
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_app_data(data: dict[str, Any]) -> None:
    """アプリデータを保存"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@router.get("", response_model=DataResponse)
def get_app_data(
    current_user: User = Depends(get_current_user)
):
    """アプリ固有データを取得"""
    data = load_app_data()
    
    # ユーザーごとにデータを分離
    user_data = data.get(current_user.id, {})
    
    return DataResponse(data=user_data)


@router.post("", status_code=201)
def create_app_data(
    item: DataItem,
    current_user: User = Depends(get_current_user)
):
    """アプリ固有データを作成"""
    data = load_app_data()
    
    # ユーザーごとにデータを分離
    if current_user.id not in data:
        data[current_user.id] = {}
    
    # キーの重複チェック
    if item.key in data[current_user.id]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "ERR-APP-TODO-001", "message": "キーが既に存在します"}
        )
    
    data[current_user.id][item.key] = item.value
    save_app_data(data)
    
    return {
        "success": True,
        "message": "データを作成しました",
        "key": item.key
    }


@router.put("/{key}")
def update_app_data(
    key: str,
    item: DataItem,
    current_user: User = Depends(get_current_user)
):
    """アプリ固有データを更新"""
    data = load_app_data()
    
    # ユーザーごとにデータを分離
    if current_user.id not in data or key not in data[current_user.id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ERR-APP-TODO-002", "message": "キーが見つかりません"}
        )
    
    data[current_user.id][key] = item.value
    save_app_data(data)
    
    return {
        "success": True,
        "message": "データを更新しました",
        "key": key
    }


@router.delete("/{key}")
def delete_app_data(
    key: str,
    current_user: User = Depends(get_current_user)
):
    """アプリ固有データを削除"""
    data = load_app_data()
    
    # ユーザーごとにデータを分離
    if current_user.id not in data or key not in data[current_user.id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "ERR-APP-TODO-002", "message": "キーが見つかりません"}
        )
    
    del data[current_user.id][key]
    save_app_data(data)
    
    return {
        "success": True,
        "message": "データを削除しました",
        "key": key
    }
