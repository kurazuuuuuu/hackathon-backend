from fastapi import FastAPI, Header, HTTPException, Depends
from dotenv import load_dotenv
from typing import Annotated
from datetime import datetime

# モデルとRDSサービスのインポート
from src.models import (
    UserGameProfile, 
    UserSaveRequest,
    UserResponse, 
    StatusResponse
)
from src.rds import rds_service
from src.auth import verify_token, AuthError

# 環境変数の読み込み (他のモジュールが読み込まれる前に実行する必要がある)
load_dotenv()

# FastAPIインスタンス作成
app = FastAPI()

@app.get("/v1/check")
async def check():
    return {"status": "ok"}

async def get_current_user_id(authorization: Annotated[str, Header()] = None):
    """
    AuthorizationヘッダーからユーザーIDを特定する
    Bearer <ID_TOKEN> 形式を想定
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        
        # トークン検証
        payload = verify_token(token)
        return payload['sub']

    except AuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.error)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

@app.put("/v1/user", response_model=StatusResponse)
async def save_user_profile(
    request: UserSaveRequest,
    user_id: str = Depends(get_current_user_id)
):
    """ユーザーデータを保存"""
    try:
        rds_service.upsert_user(user_id, request.profile)
        return {"status": "success", "updated_at": datetime.now()}
    except Exception as e:
        # DBエラーなどをハンドリング
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/user", response_model=UserResponse)
async def get_user_profile(
    user_id: str = Depends(get_current_user_id)
):
    """ユーザーデータを取得"""
    profile = rds_service.get_user(user_id)
    
    if not profile:
        # 初回などデータがない場合は新規作成扱いとして空プロフィールを返すか、404にするか
        # ここではクライアントの仕様に合わせて "初期状態" を返すことにする
        profile = UserGameProfile(
            display_name="New User",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    return {
        "status": "success",
        "user_id": user_id,
        "profile": profile
    }