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
user_sessions = {}

def main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("🛒 Browse Gear", callback_data="browse_categories"),
        InlineKeyboardButton("📋 My Bookings", callback_data="my_bookings")
    )
    return markup

def show_main_menu(chat_id):
    bot.send_message(
        chat_id,
        "🚀 **Nexus Central**\nSelect an option:",
        reply_markup=main_menu(),
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.chat.id in user_sessions:
        show_main_menu(message.chat.id)
    else:
        msg = bot.reply_to(message, "Welcome to Nexus! Please enter your registered email to log in:")
        bot.register_next_step_handler(msg, process_login)

def process_login(message):
    email = message.text.strip()
    try:
        users = requests.get(f"{API_URL}/users/").json()
        user = next((u for u in users if u['email'].lower() == email.lower()), None)
        
        if user:
            user_sessions[message.chat.id] = user['id']
            bot.send_message(message.chat.id, f"✅ Verified! Welcome back, {user['name']}.")
            show_main_menu(message.chat.id)
        else:
            msg = bot.send_message(message.chat.id, "❌ Access Denied. Email not found. Try again or contact Admin.")
            bot.register_next_step_handler(msg, process_login)
    except Exception:
        bot.send_message(message.chat.id, "API Error. Make sure the server is running.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id)

    if call.message.chat.id not in user_sessions:
        bot.send_message(call.message.chat.id, "Session expired. Type /start to log in.")
        return

    if call.data == "main_menu":
        bot.edit_message_text("🚀 **Nexus Central**\nSelect an option:", call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode='Markdown')

    elif call.data == "browse_categories":
        show_categories(call.message)

    elif call.data == "my_bookings":
        try:
            user_id = user_sessions[call.message.chat.id]
            response = requests.get(f"{API_URL}/bookings/").json()
            user_bookings = [b for b in response if b['user_id'] == user_id]
            if not user_bookings:
                text = "You have no active bookings."
            else:
                text = "📋 **Your Active Bookings:**\n\n"
                for b in user_bookings:
                    text += f"🔹 Item ID: {b['resource_id']} | Starts: {b['start_time'][:16]}\n"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode='Markdown')
        except Exception:
            bot.send_message(call.message.chat.id, "❌ Error fetching bookings.")

    elif call.data.startswith("cat_"):
        category_id = call.data.split("_")[1]
        show_resources(call.message, category_id)

    elif call.data.startswith("item_"):
        item_id = call.data.split("_")[1]
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Today", callback_data=f"date_{item_id}_0"),
            InlineKeyboardButton("Tomorrow", callback_data=f"date_{item_id}_1")
        )
        markup.add(InlineKeyboardButton("⬅️ Cancel", callback_data="browse_categories"))
        bot.edit_message_text("Select booking day:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("date_"):
        _, item_id, offset = call.data.split("_")
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Morning (10:00 - 14:00)", callback_data=f"time_{item_id}_{offset}_AM"),
            InlineKeyboardButton("Afternoon (14:00 - 18:00)", callback_data=f"time_{item_id}_{offset}_PM")
        )
        markup.add(InlineKeyboardButton("⬅️ Cancel", callback_data="browse_categories"))
        bot.edit_message_text("Select a time slot:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("time_"):
        _, item_id, offset, slot = call.data.split("_")
        
        try:
            weather = requests.get(f"{API_URL}/check-weather").json()
            weather_msg = f"🌦 **Weather Check:** {weather['message']}\n"
            warning = ""
            if not weather['safe']:
                warning = "⚠️ **WARNING:** It is raining. Outdoor gear booking might fail.\n\n"

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("✅ Confirm Booking", callback_data=f"confirm_{item_id}_{offset}_{slot}"))
            markup.add(InlineKeyboardButton("❌ Cancel", callback_data="browse_categories"))
            
            text = f"{warning}{weather_msg}\nYou are about to book Item #{item_id}. Proceed?"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(call.message.chat.id, "❌ Weather API Error.")

    elif call.data.startswith("confirm_"):
        _, item_id, offset, slot = call.data.split("_")
        user_id = user_sessions[call.message.chat.id]
        
        target_date = datetime.now() + timedelta(days=int(offset))
        if slot == "AM":
            start = target_date.strftime("%Y-%m-%dT10:00:00")
            end = target_date.strftime("%Y-%m-%dT14:00:00")
        else:
            start = target_date.strftime("%Y-%m-%dT14:00:00")
            end = target_date.strftime("%Y-%m-%dT18:00:00")

        try:
            url = f"{API_URL}/bookings/?user_id={user_id}&resource_id={item_id}&start_time={start}&end_time={end}"
            response = requests.post(url)

            if response.status_code == 200:
                bot.edit_message_text("✅ **Booking Confirmed!**\nYour gear is reserved. See you at the hub!", call.message.chat.id, call.message.message_id, reply_markup=main_menu(), parse_mode='Markdown')
            else:
                error_msg = response.json().get('detail', 'Unknown Error')
                bot.edit_message_text(f"❌ **Booking Failed:** {error_msg}", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
        except Exception:
            bot.send_message(call.message.chat.id, "❌ API Error: Is the server running?")

def show_categories(message):
    markup = InlineKeyboardMarkup()
    try:
        cats = requests.get(f"{API_URL}/resources/categories/").json()
        for c in cats:
            markup.add(InlineKeyboardButton(c['name'], callback_data=f"cat_{c['id']}"))
    except Exception:
        pass
    markup.add(InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu"))
    bot.edit_message_text("Select a Category:", message.chat.id, message.message_id, reply_markup=markup)

def show_resources(message, category_id):
    try:
        response = requests.get(f"{API_URL}/resources/").json()
        filtered = [r for r in response if str(r['category_id']) == category_id]

        markup = InlineKeyboardMarkup()
        if not filtered:
            markup.add(InlineKeyboardButton("⬅️ Back", callback_data="browse_categories"))
            bot.edit_message_text("No items available.", message.chat.id, message.message_id, reply_markup=markup)
            return

        for item in filtered:
            markup.add(InlineKeyboardButton(f"📦 {item['name']}", callback_data=f"item_{item['id']}"))

        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="browse_categories"))
        bot.edit_message_text("Select an item to book:", message.chat.id, message.message_id, reply_markup=markup)
    except Exception:
        bot.send_message(message.chat.id, "❌ Error fetching resources.")

if __name__ == "__main__":
    bot.infinity_polling()