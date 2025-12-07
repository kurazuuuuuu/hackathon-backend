# 学内ハッカソン バックエンド
## 概要
* Unity
    * ユーザーログイン認証
    * ユーザーデータ保存
    
## 技術スタック
* Python
    * uv
    * FastAPI
    * boto3

### AWS
* Aurora and RDS
* Cognito

### Cloudflare
* Cloudflare Tunnel

## 開発環境
### FastAPI
* FastAPI CLI
    * 開発環境：`uv run fastapi dev`
    * 本番環境：`uv run fastapi run`

### Python
* Pythonパッケージインストール：`uv sync`
* Pythonコードチェック：`uv run ruff check`

### Docker
* Docker Compose：`docker compose up --build -d` (-dはデタッチで起動)