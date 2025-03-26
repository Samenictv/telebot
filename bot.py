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
                return  # Allow admins to post in any topic

            # Check if the message is any of the following types
            if (message.text or message.photo or message.video or message.document or 
                message.audio or message.voice or message.sticker or message.animation):
                
                # Delete the message regardless of its type
                bot.delete_message(message.chat.id, message.message_id)

                # Send a private warning message to the user
                warning_msg = f"⚠️ @{message.from_user.username} 🚫 Only admins can post in this topic. Please use the General topic for discussions."
                
                try:
                    bot.send_message(message.from_user.id, warning_msg)
                except Exception as private_error:
                    print(f"Failed to send private message: {private_error}")

        except Exception as e:
            print("Error handling message:", e)

if __name__ == "__main__":
    print("Starting bot...")
    keep_alive()  # Keep the bot alive using Flask
    bot.infinity_polling()  # Start the bot
