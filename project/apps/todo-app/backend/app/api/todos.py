"""TODO API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# システム共通基盤のモデルをインポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "backend"))

from app.sys.models.user import User
from app.sys.core.dependencies import get_current_user

from ..models.todo import TodoCreate, TodoUpdate, TodoResponse
from ..services.todo_service import TodoService
from ..dal.todo_dal import TodoDAL

router = APIRouter()


def get_todo_dal() -> TodoDAL:
    """TodoDAL を取得"""
    return TodoDAL()


def get_todo_service(dal: TodoDAL = Depends(get_todo_dal)) -> TodoService:
    """TodoService を取得"""
    return TodoService(dal=dal)


class TodoListResponse(BaseModel):
    """TODO一覧レスポンス"""
    todos: list[TodoResponse]
    total: int
    limit: int
    offset: int


class TodoStatsResponse(BaseModel):
    """TODO統計レスポンス"""
    total: int
    completed: int
    active: int
    overdue: int


@router.get("", response_model=TodoListResponse)
def list_todos(
    completed: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    sortBy: str = Query("createdAt"),
    order: str = Query("desc"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODO一覧を取得"""
    todos, total = todo_service.list_todos(
        user_id=current_user.id,
        completed=completed,
        search=search,
        sort_by=sortBy,
        order=order,
        limit=limit,
        offset=offset
    )
    
    return TodoListResponse(
        todos=[TodoResponse(**todo.model_dump()) for todo in todos],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/stats", response_model=TodoStatsResponse)
def get_stats(
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODO統計情報を取得"""
    stats = todo_service.get_stats(current_user.id)
    return TodoStatsResponse(**stats)


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODO詳細を取得"""
    todo = todo_service.get_todo(todo_id, current_user.id)
    return TodoResponse(**todo.model_dump())


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(
    todo_create: TodoCreate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODOを作成"""
    todo = todo_service.create_todo(current_user.id, todo_create)
    return TodoResponse(**todo.model_dump())


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODOを更新"""
    todo = todo_service.update_todo(todo_id, current_user.id, todo_update)
    return TodoResponse(**todo.model_dump())


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODOを削除"""
    todo_service.delete_todo(todo_id, current_user.id)
    return {"success": True, "message": "TODOを削除しました"}


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    todo_service: TodoService = Depends(get_todo_service)
):
    """TODO完了/未完了を切り替え"""
    todo = todo_service.toggle_todo(todo_id, current_user.id)
    return TodoResponse(**todo.model_dump())
