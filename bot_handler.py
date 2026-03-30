import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = "http://127.0.0.1:8000"

bot = telebot.TeleBot(TOKEN)

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🛒 Browse Gear", callback_data="browse_categories"),
        InlineKeyboardButton("☁️ Weather Check", callback_data="check_weather"),
        InlineKeyboardButton("📋 My Bookings", callback_data="my_bookings")
    )
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🚀 **Welcome to Nexus Barcelona**\nSelect an option below to manage your gear:",
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # 🛑 THE FIX: Instantly tell Telegram we got the click to stop the loading spinner
    bot.answer_callback_query(call.id)

    if call.data == "main_menu":
        bot.edit_message_text(
            "🚀 **Welcome to Nexus Barcelona**\nSelect an option below:",
            call.message.chat.id, call.message.message_id,
            reply_markup=main_menu(), parse_mode='Markdown'
        )

    elif call.data == "browse_categories":
        show_categories(call.message)

    elif call.data == "check_weather":
        try:
            response = requests.get(f"{API_URL}/check-weather").json()
            bot.edit_message_text(f"🌦 **Barcelona Status:**\n{response['message']}",
                                  call.message.chat.id, call.message.message_id,
                                  reply_markup=main_menu(), parse_mode='Markdown')
        except Exception:
            bot.send_message(call.message.chat.id, "❌ API Error.")

    elif call.data == "my_bookings":
        try:
            response = requests.get(f"{API_URL}/bookings/").json()
            user_bookings = [b for b in response if b['user_id'] == 1]
            if not user_bookings:
                text = "You have no active bookings."
            else:
                text = "📋 **Your Active Bookings:**\n\n"
                for b in user_bookings:
                    text += f"🔹 Item ID: {b['resource_id']} | Starts: {b['start_time'][:10]}\n"
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, 
                                  reply_markup=main_menu(), parse_mode='Markdown')
        except Exception:
            bot.send_message(call.message.chat.id, "❌ Error fetching bookings.")

    elif call.data.startswith("cat_"):
        category_id = call.data.split("_")[1]
        show_resources(call.message, category_id)

    elif call.data.startswith("book_"):
        resource_id = call.data.split("_")[1]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("✅ Yes, Confirm", callback_data=f"confirm_{resource_id}"))
        markup.add(InlineKeyboardButton("❌ Cancel", callback_data="browse_categories"))

        bot.edit_message_text(f"Are you sure you want to book Resource #{resource_id} for tomorrow?",
                              call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif call.data.startswith("confirm_"):
        resource_id = int(call.data.split("_")[1])
        user_id = 1  
        
        tomorrow = datetime.now() + timedelta(days=1)
        start = tomorrow.strftime("%Y-%m-%dT10:00:00")
        end = tomorrow.strftime("%Y-%m-%dT14:00:00")

        try:
            url = f"{API_URL}/bookings/?user_id={user_id}&resource_id={resource_id}&start_time={start}&end_time={end}"
            response = requests.post(url)

            if response.status_code == 200:
                bot.edit_message_text("✅ **Booking Confirmed!**\nYour gear is reserved. See you at the hub!",
                                      call.message.chat.id, call.message.message_id,
                                      reply_markup=main_menu(), parse_mode='Markdown')
            else:
                error_msg = response.json().get('detail', 'Unknown Error')
                bot.edit_message_text(f"❌ **Booking Failed:** {error_msg}", 
                                      call.message.chat.id, call.message.message_id,
                                      reply_markup=main_menu())
        except Exception:
            bot.send_message(call.message.chat.id, "❌ API Error: Is the server running?")

def show_categories(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📸 Photo/Video Gear", callback_data="cat_1"))
    markup.add(InlineKeyboardButton("🏢 Studios", callback_data="cat_2"))
    markup.add(InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu"))

    bot.edit_message_text("Select a Category to browse:", message.chat.id, message.message_id, reply_markup=markup)

def show_resources(message, category_id):
    try:
        response = requests.get(f"{API_URL}/resources/").json()
        filtered = [r for r in response if str(r['category_id']) == category_id]

        markup = InlineKeyboardMarkup()
        if not filtered:
            markup.add(InlineKeyboardButton("⬅️ Back", callback_data="browse_categories"))
            bot.edit_message_text(f"No items available in Category {category_id} right now.", 
                                  message.chat.id, message.message_id, reply_markup=markup)
            return

        for item in filtered:
            markup.add(InlineKeyboardButton(f"📦 {item['name']}", callback_data=f"book_{item['id']}"))

        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="browse_categories"))
        bot.edit_message_text("Select an item to book:", message.chat.id, message.message_id, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, "❌ Error fetching resources.")

if __name__ == "__main__":
    print("Nexus Bot is pulse-checking... (Running)")
    bot.infinity_polling()