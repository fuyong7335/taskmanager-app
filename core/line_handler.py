# core/line_handler.py

from flask import Blueprint, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from core.sheets_handler import save_task_raw
import os

line_bp = Blueprint("line_bp", __name__)

# 環境変数（Renderやローカル）に設定しておく
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@line_bp.route("/callback", methods=["POST"])
def callback():
    """LINEからのWebhookを受け取る"""
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """LINEメッセージ受信時の処理"""
    user_message = event.message.text

    # スプレッドシートに記録
    save_task_raw(user_message)

    # 自動返信
    reply_text = f"「{user_message}」を受け取りました📘"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )
