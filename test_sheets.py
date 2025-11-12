from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Google Sheets に接続する設定
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("config/credentials.json", scope)
client = gspread.authorize(creds)

# スプレッドシート名を指定（あなたが作った名前に変更OK）
sheet = client.open("TaskManager").sheet1

# テスト書き込み
sheet.append_row(["テスト", "接続成功！"])

print("✅ Google Sheets に書き込み成功！")
