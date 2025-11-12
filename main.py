# main.py
from flask import Flask
from core.line_handler import line_bp

# Flaskアプリ本体を生成
app = Flask(__name__)

# BlueprintでLINEの処理を登録
app.register_blueprint(line_bp)

# Renderやローカルで実行するためのエントリーポイント
if __name__ == "__main__":
    # Renderはポート10000で受けるのが基本
    app.run(host="0.0.0.0", port=10000)
