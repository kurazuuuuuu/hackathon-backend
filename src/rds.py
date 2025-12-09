import boto3
import json
import os
import time
from typing import Optional
from botocore.exceptions import ClientError
from .models import UserGameProfile
from datetime import datetime

# .envから環境変数を読み込み
from dotenv import load_dotenv
load_dotenv()

# Aurora Serverless v2 コールドスタート対応の設定
# 最小インスタンス数が0の場合、起動に30-60秒程度かかる
MAX_RETRIES = 10  # 最大リトライ回数
INITIAL_RETRY_DELAY = 3  # 初回リトライ待機時間（秒）
MAX_RETRY_DELAY = 30  # 最大リトライ待機時間（秒）


class RdsDataService:
    def __init__(self):
        self.client = boto3.client(
            "rds-data",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        self.resource_arn = os.getenv("AWS_RDS_RESOURCE_ARN")
        self.secret_arn = os.getenv("AWS_RDS_SECRET_ARN")
        self.database = os.getenv("AWS_RDS_DB_NAME")

        if not self.resource_arn or not self.secret_arn:
            # 環境変数がなくても起動は許可する（実際にDBアクセスした時点でエラーになるか、メソッドがモックされる想定）
            print("Warning: DB_CLUSTER_ARN or DB_SECRET_ARN not set. DB operations will fail.")

    def execute_statement(self, sql: str, parameters: list = None):
        """
        SQL文を実行する（Aurora Serverless v2 コールドスタート対応）
        
        最小インスタンス数が0の場合、インスタンスが停止していると
        DatabaseNotFoundExceptionが発生します。その場合は指数バックオフで
        リトライし、インスタンスが自動起動するまで待機します。
        """
        if parameters is None:
            parameters = []

        retry_delay = INITIAL_RETRY_DELAY
        last_exception = None

        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.execute_statement(
                    resourceArn=self.resource_arn,
                    secretArn=self.secret_arn,
                    database=self.database,
                    sql=sql,
                    parameters=parameters,
                    includeResultMetadata=True
                )
                return response
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                
                # DatabaseNotFoundException: インスタンスが停止中
                # ServiceUnavailableError: インスタンス起動中
                if error_code in ['DatabaseNotFoundException', 'ServiceUnavailableError']:
                    last_exception = e
                    remaining_retries = MAX_RETRIES - attempt - 1
                    print(f"Aurora Serverless v2 starting up... "
                          f"(attempt {attempt + 1}/{MAX_RETRIES}, "
                          f"waiting {retry_delay}s, "
                          f"remaining retries: {remaining_retries})")
                    time.sleep(retry_delay)
                    # 指数バックオフ（最大MAX_RETRY_DELAYまで）
                    retry_delay = min(retry_delay * 1.5, MAX_RETRY_DELAY)
                else:
                    # 他のエラーは即座に再送出
                    print(f"RDS Data API Error: {e}")
                    raise e
            except Exception as e:
                print(f"RDS Data API Error: {e}")
                raise e

        # 全リトライ失敗
        print(f"RDS Data API Error: Max retries ({MAX_RETRIES}) exceeded. "
              f"Aurora Serverless v2 instance may take longer to start.")
        raise last_exception

    def initialize_db(self):
        """
        テーブル初期化（サーバー起動時に実行）
        Schema: users (id VARCHAR PRIMARY KEY, profile JSONB)
        """
        sql = """
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                profile JSONB
            );
        """
        print("Initializing database...")
        self.execute_statement(sql)
        print("Database initialized.")

    def get_user(self, user_id: str) -> Optional[UserGameProfile]:
        """
        ユーザーデータを取得する
        Table Schema Assumption: users (id VARCHAR PK, profile JSON)
        """
        sql = "SELECT profile FROM users WHERE id = :id"
        params = [{'name': 'id', 'value': {'stringValue': user_id}}]
        
        try:
            response = self.execute_statement(sql, params)
            if not response or 'records' not in response or not response['records']:
                return None
            
            # response['records'][0] -> [{'stringValue': '{"display_name": ...}'}]
            json_str = response['records'][0][0]['stringValue']
            data = json.loads(json_str)
            return UserGameProfile(**data)
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def upsert_user(self, user_id: str, profile: UserGameProfile) -> None:
        """
        ユーザーデータを保存（基本はINSERT ON CONFLICT Update）
        PostgreSQL/Aurora互換SQL
        """
        # updated_atを更新
        profile.updated_at = datetime.now()
        
        json_str = profile.model_dump_json() # Pydantic v2
        
        sql = """
            INSERT INTO users (id, profile) VALUES (:id, CAST(:profile AS JSONB))
            ON CONFLICT (id) 
            DO UPDATE SET profile = EXCLUDED.profile
        """
        params = [
            {'name': 'id', 'value': {'stringValue': user_id}},
            {'name': 'profile', 'value': {'stringValue': json_str}} # JSONB column accepts stringified JSON
        ]
        
        self.execute_statement(sql, params)

# シングルトンとしてエクスポート
rds_service = RdsDataService()


