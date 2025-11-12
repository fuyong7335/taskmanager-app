# test_save_task.py
from core.sheets_handler import save_task_raw

# テスト：このメッセージがシートに追加される
test_message = "11/15 14:00 顧客打ち合わせ"

save_task_raw(test_message)

print("✅ タスク登録テスト完了。スプレッドシートを確認してください。")
