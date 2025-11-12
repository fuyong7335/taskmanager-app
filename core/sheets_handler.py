# core/sheets_handler.py
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from gspread_formatting import CellFormat, TextFormat, format_cell_ranges
from datetime import datetime
import os, json, re

VERSION_TAG = "sheets_handler v2"  # ← バージョン印

def get_client():
    print(f"[BOOT] {VERSION_TAG}")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    return gspread.authorize(creds)

def get_tasks_sheet():
    sh = get_client().open_by_url(os.getenv("SPREADSHEET_URL"))
    return sh.worksheet("Tasks")

def save_task_raw(user_message: str):
    """
    例: '11/15 14:00 顧客打ち合わせ'
    → A:2025-11-15 / B:14:00 / C:顧客打ち合わせ / D:未完了
    """
    sheet = get_tasks_sheet()
    now_year = datetime.now().year

    text = user_message.replace("\n", " ").replace("　", " ").strip()
    date_match = re.search(r"(\d{1,2})/(\d{1,2})", text)
    time_match = re.search(r"(\d{1,2}):(\d{2})", text)

    task_date = (
        f"{now_year}-{int(date_match.group(1)):02d}-{int(date_match.group(2)):02d}"
        if date_match else datetime.now().strftime("%Y-%m-%d")
    )
    task_time = time_match.group(0) if time_match else ""

    task_text = text
    if date_match: task_text = task_text.replace(date_match.group(0), "")
    if time_match: task_text = task_text.replace(time_match.group(0), "")
    task_text = task_text.strip()

    sheet.append_row([task_date, task_time, task_text, "未完了"])
    print(f"[INFO] SAVE_TASK_OK {task_date} {task_time} {task_text}")
    return task_date, task_time, task_text

def mark_task_complete(task_keyword: str) -> bool:
    """『完了 〇〇』で該当行に打消し線＋D列=完了"""
    sheet = get_tasks_sheet()
    rows = sheet.get_all_values()
    for i, row in enumerate(rows, start=1):
        if i == 1:  # ヘッダ飛ばし
            continue
        if len(row) >= 3 and task_keyword and (task_keyword in row[2]):
            sheet.update_cell(i, 4, "完了")
            fmt = CellFormat(textFormat=TextFormat(strikethrough=True))
            format_cell_ranges(sheet, [(f"A{i}:C{i}", fmt)])
            print(f"[INFO] COMPLETE_OK row={i} key={task_keyword}")
            return True
    print(f"[WARN] COMPLETE_NOT_FOUND key={task_keyword}")
    return False
