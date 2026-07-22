import os

# Proxy dogoggoraan serveriirraa dhufu balleessuuf (Error Proxy furuuf)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import firebase_admin
from firebase_admin import credentials, db
import time

# ----------------- FIREBASE INITIALIZATION -----------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://diamond-lottery-78180-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# API Token haaraa (Railway Variable yoo jiraate irraa fudhata, yoo hin jirre kan hardcoded fayyadama)
API_TOKEN = os.environ.get('API_TOKEN', '8626785598:AAF_O_Uj06SWWA0Npq-q8L_2BfhzhDZdWMs')
ADMIN_ID = 365353683
WEB_APP_URL = 'https://gamme-430.github.io/DaimondLottery431/'

bot = telebot.TeleBot(API_TOKEN)

# ----------------- KEYBOARDS (KOFOOWWAN) -----------------

def admin_main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Waliigala Stats", callback_data="admin_stats"),
        InlineKeyboardButton("🎮 Qindaa'ina Taphaa", callback_data="admin_games"),
        InlineKeyboardButton("👤 Bulchiinsa Users", callback_data="admin_users"),
        InlineKeyboardButton("💰 Kafaltii & Baasii", callback_data="admin_finance"),
        InlineKeyboardButton("📢 Ergaa Waliigalaa", callback_data="admin_broadcast"),
        InlineKeyboardButton("⚙️ Qindaa'ina Botii", callback_data="admin_settings")
    )
    return markup

def admin_game_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🎰 Carraa Mo'annoo (%)", callback_data="game_chance"),
        InlineKeyboardButton("💵 Gatii Taphichaa (Bet)", callback_data="game_bet"),
        InlineKeyboardButton("🎁 Badhaasa Geengoo (Slots)", callback_data="game_rewards"),
        InlineKeyboardButton("🛑 Taphicha Dhaabi/Jalqabi", callback_data="game_toggle"),
        InlineKeyboardButton("🔙 Gara Menu Jalqabaa", callback_data="back_to_main")
    )
    return markup

def admin_user_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔍 User Barbaadi", callback_data="user_search"),
        InlineKeyboardButton("➕ Maallaqa Guuti", callback_data="user_add_bal"),
        InlineKeyboardButton("➖ Maallaqa Hir'isi", callback_data="user_deduct_bal"),
        InlineKeyboardButton("🚫 Block/Unblock", callback_data="user_block"),
        InlineKeyboardButton("🔙 Gara Menu Jalqabaa", callback_data="back_to_main")
    )
    return markup

def admin_finance_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📥 Gaaffii Galii (Deposits)", callback_data="fin_deposit"),
        InlineKeyboardButton("📤 Gaaffii Baasii (Withdrawals)", callback_data="fin_withdraw"),
        InlineKeyboardButton("📜 Seenaa Hunda", callback_data="fin_history"),
        InlineKeyboardButton("🔙 Gara Menu Jalqabaa", callback_data="back_to_main")
    )
    return markup

# ----------------- HANDLERS -----------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name or "User"
    
    user_ref = db.reference(f'users/{user_id}')
    if not user_ref.get():
        user_ref.set({
            'balance': 0,
            'username': username,
            'first_name': first_name,
            'joined_at': int(time.time())
        })
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🎮 Diamond Lottery Taphaadhu", web_app=WebAppInfo(url=WEB_APP_URL))
    )
    
    bot.send_message(
        message.chat.id,
        f"👋 Nagaan dhuftan **{first_name}**!\n\n"
        "💎 **Diamond Lottery** irratti carraa keessan yaaluuf cuqaasaa gadii tuqaa:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "👋 **Diamond Lottery Admin Panel nagaan dhuftan!**\n\nFilannoo keessan gadii cuqaasaa:",
            reply_markup=admin_main_menu(),
            parse_mode="Markdown"
        )
    else:
        bot.send_message(message.chat.id, "⚠️ Dhiifama, fuula kana seenuuf mirga hin qabdu!")

@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⚠️ Mirga itti fayyadamaa hin qabdu!", show_alert=True)
        return

    if call.data == "back_to_main":
        bot.edit_message_text("Filannoo keessan cuqaasaa:", call.message.chat.id, call.message.message_id, reply_markup=admin_main_menu())

    elif call.data == "admin_games":
        bot.edit_message_text("⚙️ **Qindaa'ina Spin & Wheel To'adhaa:**", call.message.chat.id, call.message.message_id, reply_markup=admin_game_menu(), parse_mode="Markdown")

    elif call.data == "admin_users":
        bot.edit_message_text("👤 **Bulchiinsa Taphattootaa:**", call.message.chat.id, call.message.message_id, reply_markup=admin_user_menu(), parse_mode="Markdown")

    elif call.data == "admin_finance":
        bot.edit_message_text("💰 **To'annoo Maallaqa Galii fi Baasii:**", call.message.chat.id, call.message.message_id, reply_markup=admin_finance_menu(), parse_mode="Markdown")

    elif call.data == "admin_stats":
        users_data = db.reference('users').get()
        total_users = len(users_data) if users_data else 0
        current_bet = db.reference('settings/bet_amount').get() or 20
        status = db.reference('settings/game_status').get() or "Bifaan Jira"

        stats_msg = f"📊 **Waliigala Data:**\n• Taphattoota Waliigalaa: {total_users}\n• Gatii Spin Ammaa: {current_bet} ETB\n• Haala Taphaa: {status}"
        bot.send_message(call.message.chat.id, stats_msg, parse_mode="Markdown")
        bot.answer_callback_query(call.id)

    elif call.data == "game_bet":
        msg = bot.edit_message_text("💵 **Gatii taphaa (Bet) haaraa galchi (ETB):**", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_change_bet)
        bot.answer_callback_query(call.id)

    elif call.data == "game_toggle":
        current_status = db.reference('settings/game_status').get() or "Bifaan Jira"
        new_status = "Dhaabbateera" if current_status == "Bifaan Jira" else "Bifaan Jira"
        db.reference('settings/game_status').set(new_status)
        bot.answer_callback_query(call.id, f"🛑 Taphichi gara '{new_status}'-tti jijjiirameera!", show_alert=True)
        bot.edit_message_text("⚙️ **Qindaa'ina Spin & Wheel To'adhaa:**", call.message.chat.id, call.message.message_id, reply_markup=admin_game_menu(), parse_mode="Markdown")

    elif call.data == "user_add_bal":
        msg = bot.edit_message_text("➕ **Dura User ID maallaqa itti guutuuf jirtu barreessi:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_balance_input, "add")
        bot.answer_callback_query(call.id)

    elif call.data == "user_deduct_bal":
        msg = bot.edit_message_text("➖ **Dura User ID maallaqa irraa hir'isuuf jirtu barreessi:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_balance_input, "deduct")
        bot.answer_callback_query(call.id)

    elif call.data == "admin_broadcast":
        msg = bot.edit_message_text("📢 **Ergaa hundaaf gadi lakkifamu barreessi:**", call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(msg, process_broadcast)
        bot.answer_callback_query(call.id)

    else:
        bot.answer_callback_query(call.id, f"Kofoon '{call.data}' gara fuulduraatti hidhama.", show_alert=True)

# ----------------- FUNCTIONS -----------------

def process_change_bet(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        new_bet = int(message.text)
        db.reference('settings/bet_amount').set(new_bet)
        bot.send_message(message.chat.id, f"✅ Gatii taphaa gara **{new_bet} ETB**-tti jijjiirameera!", reply_markup=admin_game_menu(), parse_mode="Markdown")
    except ValueError:
        msg = bot.send_message(message.chat.id, "⚠️ Dhiifama, lakkoofsa qofa galchi:")
        bot.register_next_step_handler(msg, process_change_bet)

def process_balance_input(message, action_type):
    if message.from_user.id != ADMIN_ID: return
    target_user_id = message.text.strip()

    user_ref = db.reference(f'users/{target_user_id}')
    user_data = user_ref.get()

    if not user_data:
        bot.send_message(message.chat.id, "⚠️ Dhiifama, User ID-n kun database keessatti hin argamne!", reply_markup=admin_user_menu())
        return

    action_text = "guutamu" if action_type == "add" else "hir'ifamu"
    msg = bot.send_message(message.chat.id, f"💰 Hamma maallaqa ETB {action_text} barreessi:")
    bot.register_next_step_handler(msg, process_balance_finalize, target_user_id, action_type)

def process_balance_finalize(message, target_user_id, action_type):
    if message.from_user.id != ADMIN_ID: return
    try:
        amount = int(message.text)
        user_ref = db.reference(f'users/{target_user_id}')
        current_balance = user_ref.child('balance').get() or 0

        if action_type == "add":
            new_balance = current_balance + amount
            text_success = f"✅ User {target_user_id}-f maallaqni {amount} ETB guutameera!"
        else:
            new_balance = max(0, current_balance - amount)
            text_success = f"✅ User {target_user_id} irraa maallaqni {amount} ETB hir'ifameera!"

        user_ref.child('balance').set(new_balance)
        bot.send_message(message.chat.id, f"{text_success}\n💰 Balance Ammaa: **{new_balance} ETB**", reply_markup=admin_user_menu(), parse_mode="Markdown")

        try:
            bot.send_message(target_user_id, f"🔔 Balance keessan admin-dhaan sirreeffameera.\n💰 Balance Ammaa: **{new_balance} ETB**", parse_mode="Markdown")
        except Exception:
            pass

    except ValueError:
        msg = bot.send_message(message.chat.id, "⚠️ Dhiifama, lakkoofsa qofa galchuu qabda. Deebisii yaali:")
        bot.register_next_step_handler(msg, process_balance_finalize, target_user_id, action_type)

def process_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    users_data = db.reference('users').get()
    if not users_data:
        bot.send_message(message.chat.id, "⚠️ Ergaa dabarsuuf user-oonnii database keessa hin jiran!", reply_markup=admin_main_menu())
        return

    success_count = 0
    bot.send_message(message.chat.id, "⏳ Ergaan lakkifamaa jira...")
    for user_id in users_data.keys():
        try:
            bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            success_count += 1
        except Exception:
            pass

    bot.send_message(message.chat.id, f"✅ Ergaan milkiidhaan galeera!\n• Kan ga'e: {success_count}", reply_markup=admin_main_menu())

# ----------------- SERVER AUTO-RESTART LOOP -----------------
print("🚀 Botiin Railway irratti milkiidhaan ka'eera!")

try:
    bot.remove_webhook()
    time.sleep(2)
    print("✅ Webhook durii qulqullaa'eera.")
except Exception as e:
    print(f"⚠️ Webhook balleessuu irratti: {e}")

while True:
    try:
        print("⏳ Polling jalqabaa jira...")
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        print(f"🔴 Error uumame: {e}. Sekondii 5 booda deebi'ee eegala...")
        time.sleep(5)
