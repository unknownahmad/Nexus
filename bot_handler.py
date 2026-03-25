import os
import telebot
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://127.0.0.1:8000" # This points to your running FastAPI server

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # This identifies you specifically in the terminal
    
    
    print(f"User {message.from_user.first_name} just started the bot!")
    
    welcome_text = (
        "🚀 **Nexus Barcelona: Online**\n\n"
        "Hello Ahmad! System is connected to Google Cloud (Madrid).\n\n"
        "**Available Commands:**\n"
        "🔹 /weather - Check if outdoor gear is safe to book\n"
        "🔹 /status - Check if the API is breathing\n"
        "🔹 /help - Show this menu"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

if __name__ == "__main__":
    print("Nexus Bot is starting... (Press Ctrl+C to stop)")
    bot.infinity_polling()