# FastAPI エンドポイント
## Unity
### ユーザーログイン認証
- **Method:** `POST`
- **Path:** `/v1/user/login`
- **Request Body:**
  ```json
  {
    "username": "string",
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

### ユーザーデータ保存
- **Method:** `POST`
- **Path:** `/v1/user/save`
- **Headers:**
  - `Authorization`: `Bearer <id_token>`
- **Request Body:**
  ```json
  {
    "save_data": {
      // 任意のJSONデータ
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