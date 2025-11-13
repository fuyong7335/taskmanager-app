import os
import re
from datetime import datetime
import pytz
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from sheets import add_task, mark_done, tasks_on
from formatter import format_task_list, format_added, format_done

JST = pytz.timezone("Asia/Tokyo")

# Blueprint作成（これが最重要）
line_bp = Blueprint("line_bp", __name__)

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# パターン①：年-月-日
TASK_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})\s+(.+)")
# パターン②：MM/DD
TASK_PATTERN2 = re.compile(r"^(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})\s+(.+)")

HELP = (
    "📌 使い方\n"
    "・YYYY-MM-DD HH:MM タスク内容\n"
    "・MM/DD HH:MM タスク内容\n"
    "・今日 → 本日のタスク\n"
    "・完了 123 → 完了処理"
)


# =====================================
# callback（Blueprint版）
# =====================================
@line_bp.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


# =====================================
# handle_message（Blueprint版）
# =====================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    text = (event.message.text or "").strip()

    # ① MM/DD
    m2 = TASK_PATTERN2.match(text)
    if m2:
        month, day, time_str, content = m2.groups()
        year = datetime.now(JST).year
        d = f"{year}-{int(month):02d}-{int(day):02d}"
        t = time_str

        tid = add_task(d, t, content, source="LINE")
        if str(tid).startswith("W:"):
            exist_id = tid.split(":")[1]
            msg = f"⚠️ {d} {t} は既にID:{exist_id}があります（ダブルブッキング回避）"
        else:
            msg = format_added(tid, d, t, content)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        return

    # ② YYYY-MM-DD
    m = TASK_PATTERN.match(text)
    if m:
        d, t, content = m.groups()
        tid = add_task(d, t, content, source="LINE")
        if str(tid).startswith("W:"):
            exist_id = tid.split(":")[1]
            msg = f"⚠️ {d} {t} は既にID:{exist_id}があります（ダブルブッキング回避）"
        else:
            msg = format_added(tid, d, t, content)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        return

    # 今日
    if text in ["今日", "きょう", "本日"]:
        today = datetime.now(JST).date()
        rows = tasks_on(today)
        msg = format_task_list(today.strftime("%Y-%m-%d"), rows)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        return

    # 完了
    if text.startswith("完了 "):
        try:
            tid = int(text.split(" ", 1)[1])
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="IDは数字で指定してね"))
            return

        ok = mark_done(tid)
        msg = format_done(tid, ok)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
        return

    # ヘルプ
    if text in ["help", "ヘルプ", "使い方"]:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=HELP))
        return

    # それ以外
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="認識できませんでした。\n" + HELP)
    )
