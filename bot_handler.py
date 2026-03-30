import os
import telebot
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://127.0.0.1:8000"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🚀 **Nexus Barcelona: Online**\n\n"
        "**Available Commands:**\n"
        "🔹 /weather - Check weather safety\n"
        "🔹 /book <user_id> <resource_id> - Book gear (Demo Time)\n"
        "🔹 /help - Show this menu"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['weather'])
def check_weather(message):
    try:
        response = requests.get(f"{API_URL}/check-weather")
        data = response.json()
        bot.reply_to(message, data["message"])
    except Exception:
        bot.reply_to(message, "API offline.")

@bot.message_handler(commands=['book'])
def book_gear(message):
    try:
        parts = message.text.split()
        if len(parts) != 3:
            bot.reply_to(message, "Format: /book <user_id> <resource_id>")
            return
            
        user_id = int(parts[1])
        resource_id = int(parts[2])
        
        start_time = "2026-04-05T10:00:00"
        end_time = "2026-04-05T14:00:00"
        
        url = f"{API_URL}/bookings/?user_id={user_id}&resource_id={resource_id}&start_time={start_time}&end_time={end_time}"
        response = requests.post(url)
        
        if response.status_code == 200:
            bot.reply_to(message, "Booking successful!")
        else:
            bot.reply_to(message, f"Failed: {response.json()['detail']}")
    except ValueError:
        bot.reply_to(message, "IDs must be numbers.")
    except Exception:
        bot.reply_to(message, "API error.")

if __name__ == "__main__":
    bot.infinity_polling()