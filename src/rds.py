import boto3
import json
import os
from typing import Optional
from .models import UserGameProfile
from datetime import datetime

# .envから環境変数を読み込み
# load_dotenv() # main.pyで読み込まれる想定だが、念のためここでも使えるようにしておくかは構成次第。
# 今回はmain.pyで読み込んでいるのでここでは省略、またはmain.pyが実行エントリポイントであることを前提とする。

class RdsDataService:
    def __init__(self):
        self.client = boto3.client(
            "rds-data",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
        self.resource_arn = os.getenv("DB_CLUSTER_ARN")
        self.secret_arn = os.getenv("DB_SECRET_ARN")
        self.database = os.getenv("DB_NAME", "hackathon_db") # デフォルトDB名

        if not self.resource_arn or not self.secret_arn:
            # 環境変数がなくても起動は許可する（実際にDBアクセスした時点でエラーになるか、メソッドがモックされる想定）
            print("Warning: DB_CLUSTER_ARN or DB_SECRET_ARN not set. DB operations will fail.")

    def execute_statement(self, sql: str, parameters: list = None):
        if parameters is None:
            parameters = []

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
        except Exception as e:
            print(f"RDS Data API Error: {e}")
            raise e

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
        MySQL/Aurora互換SQLを想定
        """
        # updated_atを更新
        profile.updated_at = datetime.now()
        
        json_str = profile.model_dump_json() # Pydantic v2
        
        sql = """
            INSERT INTO users (id, profile) VALUES (:id, :profile)
            ON DUPLICATE KEY UPDATE profile = :profile
        """
        params = [
            {'name': 'id', 'value': {'stringValue': user_id}},
            {'name': 'profile', 'value': {'stringValue': json_str}}
        ]
        
        self.execute_statement(sql, params)

# シングルトンとしてエクスポート
rds_service = RdsDataService()


