# Python / FastAPI 規約

## プロジェクト構成

```
python/
  src/
    main.py           ← FastAPI アプリ起動
    routers/          ← エンドポイント定義（1ドメイン1ファイル）
    services/         ← ビジネスロジック
    models/           ← Pydantic モデル
    dependencies.py   ← 共通依存性（認証確認など）
    config.py         ← 設定（pydantic-settings）
  tests/
  .env                ← 環境変数（Git 管理外）
  .env.example        ← テンプレート（Git 管理対象）
```

## 必須パッケージ

```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-jose[cryptography]  # JWT 検証
```

## 環境変数管理（ハードコード禁止）

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    php_api_key: str          # PHP から FastAPI への認証キー
    secret_key: str           # JWT 署名キー
    allowed_origins: list[str] = ["http://localhost"]

    class Config:
        env_file = ".env"

settings = Settings()
```

## リクエスト/レスポンス バリデーション（Pydantic 必須）

```python
# models/analysis.py
from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    data: list[float] = Field(..., min_length=1)
    method: str = Field(..., pattern="^(mean|median|mode)$")

class AnalysisResponse(BaseModel):
    result: float
    method: str
```

## エンドポイント定義パターン

```python
# routers/analysis.py
from fastapi import APIRouter, Depends
from ..dependencies import verify_php_api_key
from ..models.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("/run", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest,
    _: None = Depends(verify_php_api_key),  # 認証
) -> AnalysisResponse:
    ...
```

## PHP ↔ FastAPI 認証

PHP から FastAPI を呼ぶ際は `X-Api-Key` ヘッダーで内部APIキーを使用する:

```python
# dependencies.py
from fastapi import Header, HTTPException
from .config import settings

async def verify_php_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.php_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")
```

## エラーレスポンス統一形式

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
    )
```
