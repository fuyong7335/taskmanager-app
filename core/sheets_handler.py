from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime
import os, json, re

def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    return client

def get_tasks_sheet():
    client = get_client()
    sh = client.open_by_url(os.getenv("SPREADSHEET_URL"))
    return sh.worksheet("Tasks")

def save_task_raw(user_message: str):
    """
    例: "11/15 14:00 顧客打ち合わせ"
    → A:2025-11-15 / B:14:00 / C:顧客打ち合わせ / D:未完了
    """
    sheet = get_tasks_sheet()
    now_year = datetime.now().year

    # 改行・全角スペースを整える
    text = user_message.replace("\n", " ").replace("　", " ").strip()

    # 日付（例: 11/15）と時刻（例: 14:00）を抽出
    date_match = re.search(r"(\d{1,2})/(\d{1,2})", text)
    time_match = re.search(r"(\d{1,2}):(\d{2})", text)

    task_date = (
        f"{now_year}-{int(date_match.group(1)):02d}-{int(date_match.group(2)):02d}"
        if date_match else datetime.now().strftime("%Y-%m-%d")
    )
    task_time = time_match.group(0) if time_match else ""
    
    # タスク内容部分（日時以外の文字列）
    task_part = text
    if date_match:
        task_part = task_part.replace(date_match.group(0), "")
    if time_match:
        task_part = task_part.replace(time_match.group(0), "")
    task_part = task_part.strip()

    # スプレッドシートに追記
    sheet.append_row([task_date, task_time, task_part, "未完了"])

    # LINE返信用
    return task_date, task_time, task_part
# 末尾に追加（既にあればOK）
from gspread_formatting import CellFormat, TextFormat, format_cell_ranges

def mark_task_complete(task_keyword: str) -> bool:
    """「完了 〇〇」で該当行を打消し線＋D列=完了にする"""
    sheet = get_tasks_sheet()
    records = sheet.get_all_values()
    for i, row in enumerate(records, start=1):
        if i == 1:  # ヘッダを飛ばす
            continue
        if len(row) >= 3 and task_keyword and (task_keyword in row[2]):
            sheet.update_cell(i, 4, "完了")
            fmt = CellFormat(textFormat=TextFormat(strikethrough=True))
            format_cell_ranges(sheet, [(f"A{i}:C{i}", fmt)])
            return True
    return False

