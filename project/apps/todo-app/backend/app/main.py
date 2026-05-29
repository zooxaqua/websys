"""TODOアプリ FastAPI アプリケーション"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import todos

app = FastAPI(
    title="TODOアプリ",
    version="1.0.0",
    description="タスク管理アプリケーション"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API ルーター
app.include_router(todos.router, prefix="/api/todo-app/todos", tags=["TODO"])

@app.get("/api/todo-app/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "message": "TODOアプリは正常に動作しています"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
