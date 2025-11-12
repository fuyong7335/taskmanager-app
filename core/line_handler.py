# core/line_handler.py
import os, traceback
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from core.sheets_handler import save_task_raw, mark_task_complete

VERSION_TAG = "line_handler v2"  # ← バージョン印
print(f"[BOOT] {VERSION_TAG}")

line_bp = Blueprint("line_bp", __name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@line_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("[ERROR] handler.handle failed:", e)
        print(traceback.format_exc())
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    print(f"[IN ] {user_message}")

    # 完了: 「完了 〇〇」
    if user_message.startswith("完了"):
        keyword = user_message.replace("完了", "", 1).strip()
        try:
            ok = mark_task_complete(keyword)
            reply = f"✅『{keyword}』を完了にしました！" if ok else "該当タスクが見つかりませんでした。"
        except Exception as e:
            print("[ERROR] complete failed:", e)
            print(traceback.format_exc())
            reply = "完了処理でエラーが発生しました。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 追加: 日付/時間/内容に分解して保存＋整形返信
    try:
        task_date, task_time, task_text = save_task_raw(user_message)
        reply = (
            "✅ タスク登録しました！\n"
            f"📅 日付：{task_date}\n"
            f"🕒 時間：{task_time or '未指定'}\n"
            f"📝 内容：{task_text}"
        )
    except Exception as e:
        print("[ERROR] save_task_raw failed:", e)
        print(traceback.format_exc())
        reply = "タスク登録でエラーが発生しました。設定を確認してください。"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
