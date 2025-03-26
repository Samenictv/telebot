import telebot
from flask import Flask
from threading import Thread
import os
import time

# Flask server to keep the bot alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Get the Telegram Bot Token and Allowed Topic ID from environment variables
API_TOKEN = os.getenv('API_TOKEN')  
provided_topic = os.getenv('ALLOWED_TOPIC_ID')  

try:
    ALLOWED_TOPIC_ID = int(provided_topic.split("_")[1])
    print(f"Allowed topic thread id (for #General) set to: {ALLOWED_TOPIC_ID}")
except Exception as e:
    print("Error parsing allowed topic id:", e)
    ALLOWED_TOPIC_ID = None

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: message.chat.type == 'supergroup')
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
                f"⚠️ @{message.from_user.username} 🚫 Only admins can post in this topic. Please use General topic (https://t.me/c/{provided_topic.split('_')[0]}/1) for discussions.",
                message_thread_id=message.message_thread_id
            )

            def delete_warning():
                try:
                    time.sleep(60)  # Wait 1 minute before deleting the warning
                    bot.delete_message(message.chat.id, warning_msg.message_id)
                except Exception as del_error:
                    print(f"Error deleting warning message: {del_error}")

            Thread(target=delete_warning).start()
        except Exception as e:
            print("Error handling message:", e)

if name == "__main__":
    print("Starting bot...")
    keep_alive()  # Keep the bot alive using Flask
    bot.infinity_polling()  # Start the bot
