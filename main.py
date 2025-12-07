from fastapi import FastAPI
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# FastAPIインスタンス作成
app = FastAPI()

@app.get("/v1/check")
async def check():
    return {"status": "ok"}