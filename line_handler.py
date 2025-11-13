import os
from sheets import add_task, mark_done, tasks_on
from formatter import format_task_list, format_added, format_done


JST = pytz.timezone("Asia/Tokyo")
app = Flask(__name__)
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


TASK_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})\s+(.+)")
HELP = (
"📌 使い方\n"
"・YYYY-MM-DD HH:MM タスク内容 → 追加\n"
"・今日 → 本日のタスクを表示\n"
"・完了 123 → ID=123を完了"
)


@app.route("/callback", methods=["POST"])
def callback():
signature = request.headers.get("X-Line-Signature")
body = request.get_data(as_text=True)
try:
handler.handle(body, signature)
except InvalidSignatureError:
abort(400)
return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
text = (event.message.text or "").strip()


m = TASK_PATTERN.match(text)
if m:
d, t, content = m.groups()
tid = add_task(d, t, content, source="LINE")


if isinstance(tid, str) and tid.startswith("W:"):
exist_id = tid.split(":")[1]
msg = f"⚠️ {d} {t} は既にID:{exist_id}のタスクがあります（ダブルブッキング回避）。"
else:
msg = format_added(tid, d, t, content)
line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
return


if text in ["今日", "きょう", "本日"]:
today = datetime.now(JST).date()
rows = tasks_on(today)
msg = format_task_list(today.strftime("%Y-%m-%d"), rows)
line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
return


if text.startswith("完了 "):
try:
tid = int(text.split(" ", 1)[1])
except ValueError:
line_bot_api.reply_message(event.reply_token, TextSendMessage(text="IDは数値で指定してね。例：完了 12"))
return
ok = mark_done(tid)
line_bot_api.reply_message(event.reply_token, TextSendMessage(text=format_done(tid, ok)))
return


if text in ["help", "ヘルプ", "使い方"]:
line_bot_api.reply_message(event.reply_token, TextSendMessage(text=HELP))
return


line_bot_api.reply_message(event.reply_token, TextSendMessage(text="認識できませんでした。\n" + HELP))


if __name__ == "__main__":
app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))