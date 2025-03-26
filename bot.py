import telebot
from flask import Flask, request
import os
import threading
import time

# Load token from environment variables
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Example: https://your-app.onrender.com

# Flask server for webhook
app = Flask(__name__)
bot = telebot.TeleBot(API_TOKEN, threaded=True)

provided_topic = os.getenv("ALLOWED_TOPIC", "-1002333606264_1")
try:
    ALLOWED_TOPIC_ID = int(provided_topic.split("_")[1])
    print(f"Allowed topic thread id (for #General) set to: {ALLOWED_TOPIC_ID}")
except Exception as e:
    print("Error parsing allowed topic id:", e)
    ALLOWED_TOPIC_ID = None

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

@bot.message_handler(func=lambda message: message.chat.type == 'supergroup', content_types=['text', 'document', 'photo', 'video', 'audio', 'voice', 'video_note', 'sticker'])
def restrict_message(message):
    if message.is_topic_message:
        topic_id = message.message_thread_id
        if topic_id == ALLOWED_TOPIC_ID:
            return
        
        try:
            member = bot.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in ['administrator', 'creator']:
                return
            
            bot.delete_message(message.chat.id, message.message_id)
            warning_msg = bot.send_message(
                message.chat.id,
                f"⚠️ @{message.from_user.id}\n🚫 Only admins can post in this topic. Please use General topic (https://t.me/c/2333606264/1) for discussions.",
                message_thread_id=message.message_thread_id
            )
            
            def delete_warning():
                time.sleep(60)
                bot.delete_message(message.chat.id, warning_msg.message_id)
            
            threading.Thread(target=delete_warning).start()
        except Exception as e:
            print("Error handling message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
