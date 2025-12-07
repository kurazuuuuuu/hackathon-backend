# FastAPI エンドポイント
## Unity
### ヘルスチェック
- **Method:** `GET`
- **Path:** `/v1/check`
- **Response:**
  ```json
  {
    "status": "ok"
  }
  ```
  
### ユーザーログイン認証
- **Method:** `POST`
- **Path:** `/v1/user/login`
- **Request Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "string",
    "id_token": "string",
    "refresh_token": "string"
  }
  ```

### ユーザーデータ関連
#### 保存
- **Method:** `PUT`
- **Path:** `/v1/user`
- **Headers:**
  - `Authorization`: `Bearer <id_token>`
- **Request Body:**
  ```json
  {
    "profile": {
      "display_name": "Hero",
      "ticket": 100,
      "cards": [
        {
          "card_id": "card_001",
          "amount": 1
        }
      ],
      "decks": [
        {
          "deck_id": "deck_1",
          "name": "My Best Deck",
          "primary_cards": ["hero_01", "hero_02", "hero_03"],
          "secondary_cards": ["support_01", "support_02"]
        }
      ],
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-02T10:00:00"
    }
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "updated_at": "datetime"
  }
  ```

#### 取得
- **Method:** `GET`
- **Path:** `/v1/user`
- **Headers:**
  - `Authorization`: `Bearer <id_token>`
- **Request Body:** なし
- **Response:**
  ```json
  {
    "status": "success",
    "user_id": "string",
    "profile": {
      "display_name": "Hero",
      "ticket": 100,
      "cards": [
        {
          "card_id": "card_001",
          "amount": 1
        }
      ],
      "decks": [
        {
          "deck_id": "deck_1",
          "name": "My Best Deck",
          "primary_cards": ["hero_01", "hero_02", "hero_03"],
          "secondary_cards": ["support_01", "support_02"]
        }
      ],
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-02T10:00:00"
    }
  }
  ```