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

# Get API Token and Allowed Topic ID from environment variables
API_TOKEN = os.getenv('API_TOKEN')
provided_topic = os.getenv('ALLOWED_TOPIC_ID')

try:
    ALLOWED_TOPIC_ID = int(provided_topic.split("_")[1])
    print(f"Allowed topic thread id (for #General) set to: {ALLOWED_TOPIC_ID}")
except Exception as e:
    print("Error parsing allowed topic id:", e)
    ALLOWED_TOPIC_ID = None

bot = telebot.TeleBot(API_TOKEN)

# Delete webhook before starting the bot (recommended)
bot.delete_webhook()

@bot.message_handler(
    func=lambda message: message.chat.type == 'supergroup', 
    content_types=['text', 'document', 'photo', 'video', 'audio', 'voice', 'video_note', 'sticker']
)
def restrict_message(message):
    if message.is_topic_message:
        topic_id = message.message_thread_id

        # Allow messages only in the allowed topic (#General)
        if topic_id == ALLOWED_TOPIC_ID:
            return

        try:
            # Check the sender's status in the group
            member = bot.get_chat_member(message.chat.id, message.from_user.id)

            # Allow admins to post in all topics
            if member.status in ['administrator', 'creator']:
                return

            # Delete the message from non-admins in restricted topics
            bot.delete_message(message.chat.id, message.message_id)

            # Send a private warning to the user
            warning_msg = f"⚠️ @{message.from_user.username}\n🚫 Only admins can post in this topic. Please use General topic for discussions."
            try:
                bot.send_message(message.from_user.id, warning_msg)
            except:
                print("Could not send a private message to the user.")

        except Exception as e:
            print(f"Error handling message: {e}")

if __name__ == "__main__":
    print("Starting bot...")
    keep_alive()  # Keep the Flask server running
    bot.infinity_polling()  # Start the bot
