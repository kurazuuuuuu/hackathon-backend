import os
from unittest.mock import MagicMock
# 実際の動作確認のため、必要であればここで環境変数をセット
# src/rds.pyの初期化でエラーにならなくなったため、環境変数がなくてもテスト可能

from fastapi.testclient import TestClient
from main import app
from src.rds import rds_service
from src.models import UserGameProfile
from datetime import datetime


# モックの設定 (AWSに接続しないようにする)
# 実際のAWS接続テストを行いたい場合は、このモックを無効化してください
mock_profile = {
    "display_name": "Test User",
    "ticket": 100,
    "cards": [{"card_id": "c1", "amount": 1}],
    "decks": [],
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
}
rds_service.get_user = MagicMock(return_value=UserGameProfile(**mock_profile))
rds_service.upsert_user = MagicMock(return_value=None)

client = TestClient(app)

def test_api():
    print("--- Starting API Verification ---")

    # 1. Health Check
    print("\n1. Testing GET /v1/check...")
    res = client.get("/v1/check")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

    # 2. Login
    print("\n2. Testing POST /v1/user/login...")
    res = client.post("/v1/user/login")
    print(f"Status: {res.status_code}")
    data = res.json()
    print(f"Response: {data}")
    assert res.status_code == 200
    assert "id_token" in data
    id_token = data["id_token"]

    # 3. Save User Profile
    print("\n3. Testing PUT /v1/user...")
    auth_header = {"Authorization": f"Bearer {id_token}"}
    payload = {
        "profile": {
            "display_name": "Updated Hero",
            "ticket": 200,
            "cards": [],
            "decks": []
        }
    }
    res = client.put("/v1/user", json=payload, headers=auth_header)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # 4. Get User Profile
    print("\n4. Testing GET /v1/user...")
    res = client.get("/v1/user", headers=auth_header)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    # モックデータが返るはず
    assert res.json()["profile"]["display_name"] == "Test User" 

    print("\n--- Verification Completed Successfully ---")

if __name__ == "__main__":
    test_api()
