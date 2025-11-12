# core/sheets_handler.py

from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime

# Google Sheets に接続するクライアントを取得
def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "config/credentials.json",
        scope
    )
    client = gspread.authorize(creds)
    return client

# Tasksシートを取得（なければ手動で作成しておく）
def get_tasks_sheet():
    client = get_client()
    # スプレッドシート名はあなたが作った名前に合わせる
    sh = client.open("TaskManager")
    sheet = sh.worksheet("Tasks")
    return sheet

# タスクを1件保存する（今はテキストをそのまま入れる簡易版）
def save_task_raw(user_message: str):
    """
    例: "11/15 14:00 顧客打ち合わせ"
    といった文字列を、そのまま1行として保存するテスト用。
    後で正式フォーマットに分解する。
    """
    sheet = get_tasks_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 今は暫定で「メッセージ全文」と「登録日時」だけ入れる
    sheet.append_row([user_message, now])
