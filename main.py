from fastapi import FastAPI

# FastAPIインスタンス作成
app = FastAPI()


@app.get("/v1/check")
async def check():
    return {"status": "ok"}