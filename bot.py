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

            # Send warning in the same topic and delete after 1 minute
            warning_msg = bot.send_message(
                message.chat.id,
                f"⚠️ @{message.from_user.id}\n🚫 Only admins can post in this topic. Please use General topic (https://t.me/c/2333606264/1) for discussions.",
                message_thread_id=message.message_thread_id
            )
            
            # Schedule message deletion after 10 sec
            def delete_warning():
                try:
                    bot.delete_message(message.chat.id, warning_msg.message_id)
                except Exception as del_error:
                    print(f"Error deleting warning message: {del_error}")
            
            Thread(target=lambda: (time.sleep(10), delete_warning())).start()
        except Exception as e:
            print("Error handling message:", e)
if __name__ == "__main__":
    print("Starting bot with webhook...")
    keep_alive()  # Keep the Flask server running
    WEBHOOK_URL = "https://telebot-fx5i.onrender.com"  # Start the bot
    bot.remove_webhook()
    time.sleep(1)  # To ensure the webhook is removed
    bot.set_webhook(url=WEBHOOK_URL)
