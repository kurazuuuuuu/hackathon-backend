from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# ==========================================
# データモデルの定義 (Schemas)
# ==========================================
# ここでは、APIでやり取りするデータの「形」を定義します。
# Pydantic (BaseModel) を使うことで、データの自動検証（バリデーション）が行われます。

class Card(BaseModel):
    # カード本体のモデル（所持数管理用）
    card_id: str
    amount: int


class Deck(BaseModel):
    """
    デッキ編成のモデル
    
    制約:
    - primary: 3枚 (固定)
    - support + special: 合計20枚
    """
    deck_id: str
    name: str
    # Primaryカード (3枚)
    primary_cards: List[str] = [] 
    # Support / Specialカード (合計20枚)
    secondary_cards: List[str] = []


class UserGameProfile(BaseModel):
    """
    Unityユーザーのゲームデータ構造(RDS用)
    
    RDS(リレーショナルデータベース)では、検索や集計によく使う項目は「カラム(列)」として定義し、
    中身が変わりやすいデータや複雑なデータは「JSON型」としてまとめて保存するのが定石です。
    """
    # ----------------------------------------------------------------
    # [Structured Columns] 構造化データ
    # データベースの「列」として保存します。
    # 検索(WHERE句)や、集計(SUM/AVG)・並び替え(ORDER BY)が高速にできます。
    # ----------------------------------------------------------------
    display_name: str  # プレイヤー名
    ticket: int = 0    # ガチャチケットなどの重要通貨など
    
    # ----------------------------------------------------------------
    # [JSON Column] 非構造化データ
    # データベースには「JSON形式のテキスト」としてまとめて保存します。
    # ゲームの仕様変更で中身が増減しても、データベースの定義変更(マイグレーション)が不要で楽です。
    # ----------------------------------------------------------------
    cards: List[Card] = []  # 所持カード一覧
    decks: List[Deck] = []  # デッキ一覧
    current_deck_id: Optional[str] = None # 現在使用中のデッキID
    
    # ----------------------------------------------------------------
    # [Meta] 管理情報
    # いつ作成・更新されたかの日時情報です。
    # Optional[datetime] = None は、「データがない(None)ことも許容する」という意味です。
    # 基本的にサーバー側で自動設定するので、リクエスト時には空でOKです。
    # ----------------------------------------------------------------
    created_at: Optional[datetime] = None  # アカウント作成日時
    updated_at: Optional[datetime] = None  # データ最終更新日時


class UserSaveRequest(BaseModel):
    """
    ユーザーデータを保存(PUT)する時のリクエスト形式
    """
    profile: UserGameProfile


class UserResponse(BaseModel):
    """
    ユーザーデータを取得(GET)した時のレスポンス形式
    """
    status: str              # "success" などの状態
    user_id: str             # ユーザーID (CognitoなどのID)
    profile: UserGameProfile # ゲームデータ本体


class StatusResponse(BaseModel):
    """
    保存成功時などに状態だけを返すシンプルなレスポンス
    """
    status: str
    updated_at: datetime     # 更新された日時
