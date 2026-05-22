import os
import json
import logging
from flask import Flask, send_from_directory, request
import requests

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder="static")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GAME_URL = os.environ.get("GAME_URL", "")  # e.g. https://your-app.railway.app

# ── Serve the game ────────────────────────────────────────────────────────────

@app.route("/")
def serve_game():
    return send_from_directory("static", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

# ── Telegram Bot Webhook ──────────────────────────────────────────────────────

def tg_api(method, **kwargs):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    r = requests.post(url, json=kwargs)
    return r.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    logging.info("Update: %s", json.dumps(data)[:300])

    # Handle regular messages
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        first_name = msg.get("from", {}).get("first_name", "Player")

        if text in ("/start", "/play"):
            send_game_launch(chat_id, first_name)
        elif text == "/help":
            tg_api("sendMessage",
                chat_id=chat_id,
                text=(
                    "🔢 *Make a Number* — How to play:\n\n"
                    "You get 4 number cards and 4 operations (+−×÷).\n"
                    "Combine cards step by step to reach the *target number*.\n\n"
                    "• Tap a number → tap an operation → tap another number\n"
                    "• The two cards merge into one result card\n"
                    "• Keep going until one card remains\n"
                    "• Score points — fewer steps = more points!\n\n"
                    "Tap /play to start! 🚀"
                ),
                parse_mode="Markdown"
            )
        else:
            send_game_launch(chat_id, first_name)

    # Handle Mini App data sent back from the game (game over score)
    if "message" in data and "web_app_data" in data.get("message", {}):
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        raw = msg["web_app_data"]["data"]
        try:
            payload = json.loads(raw)
            score = payload.get("score", 0)
            rounds = payload.get("rounds", 10)
            stars = "⭐⭐⭐" if score >= 350 else "⭐⭐" if score >= 200 else "⭐"
            tg_api("sendMessage",
                chat_id=chat_id,
                text=(
                    f"🏆 *Game finished!*\n\n"
                    f"You scored *{score} points* over {rounds} rounds!\n{stars}\n\n"
                    f"Play again? 👇"
                ),
                parse_mode="Markdown",
                reply_markup={
                    "inline_keyboard": [[{
                        "text": "🎮 Play Again",
                        "web_app": {"url": GAME_URL}
                    }]]
                }
            )
        except Exception as e:
            logging.error("Error parsing web app data: %s", e)

    return "ok", 200

def send_game_launch(chat_id, first_name):
    tg_api("sendMessage",
        chat_id=chat_id,
        text=(
            f"Hey {first_name}! 👋\n\n"
            f"🔢 *Make a Number* is ready to play!\n\n"
            f"You'll get 4 number cards and need to combine them "
            f"using +−×÷ to reach the target. 10 rounds, go for the high score! 🏆"
        ),
        parse_mode="Markdown",
        reply_markup={
            "inline_keyboard": [[{
                "text": "🎮 Play Now",
                "web_app": {"url": GAME_URL}
            }]]
        }
    )

# ── Setup webhook on startup ──────────────────────────────────────────────────

@app.route("/setup")
def setup_webhook():
    if not BOT_TOKEN or not GAME_URL:
        return "Missing BOT_TOKEN or GAME_URL env vars", 400
    webhook_url = f"{GAME_URL}/webhook"
    result = tg_api("setWebhook", url=webhook_url)
    # Set bot commands
    tg_api("setMyCommands", commands=[
        {"command": "start", "description": "Start the bot"},
        {"command": "play",  "description": "Launch the game"},
        {"command": "help",  "description": "How to play"},
    ])
    return f"Webhook set: {result}", 200

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
