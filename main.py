import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, PreCheckoutQuery
from config import TOKEN, TELEGRAM_PAYMENT_PROVIDER_TOKEN, MIN_DONATION
from payment import get_cryptobot_pay_link, check_cryptobot_payment_status, get_yoomoney_pay_link, check_yoomoney_payment_status
from publication import complete_donation

bot = telebot.TeleBot(TOKEN)
pending_cryptobot = {}
pending_yoomoney = {}

@bot.message_handler(commands=["start"])
def start(message):
    username = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"Приветствую, {username}! 😊\nВы здесь, чтобы помочь развитию нашего канала!\n\nВведите сумму для доната (минимум {MIN_DONATION}₽):"
    )

@bot.message_handler(func=lambda m: m.text and m.text.isdigit())
def handle_donation_amount(message):
    try:
        amount = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Пожалуйста, введите корректное число.")
        return
    if amount < MIN_DONATION:
        bot.send_message(message.chat.id, f"❌ Минимальная сумма доната {MIN_DONATION}₽.")
        return
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("💰 Cryptobot", callback_data=f"donate_cryptobot_{amount}"),
        InlineKeyboardButton("💳 YooMoney", callback_data=f"donate_yoomoney_{amount}")
    )
    markup.add(InlineKeyboardButton("⭐ Telegram Stars", callback_data=f"donate_stars_{amount}"))
    bot.send_message(message.chat.id, "Выберите способ оплаты для доната:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("donate_"))
def process_donation_method(call):
    chat_id = call.message.chat.id
    username = call.from_user.first_name
    data = call.data.split("_")
    method = data[1]
    try:
        amount = int(data[2])
    except Exception:
        bot.answer_callback_query(call.id, "Ошибка обработки суммы.")
        return
    if method == "cryptobot":
        pay_url, invoice_id = get_cryptobot_pay_link(amount)
        if pay_url and invoice_id:
            pending_cryptobot[invoice_id] = {
                "chat_id": chat_id,
                "amount": amount,
                "username": username,
                "method": "Cryptobot",
                "message_id": call.message.message_id
            }
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🔗 Оплатить Cryptobot", url=pay_url))
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, "❌ Ошибка создания платежа Cryptobot. Попробуйте позже.")
    elif method == "yoomoney":
        pay_url, label = get_yoomoney_pay_link(amount, chat_id)
        pending_yoomoney[label] = {
            "chat_id": chat_id,
            "amount": amount,
            "username": username,
            "method": "YooMoney",
            "message_id": call.message.message_id
        }
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔗 Оплатить YooMoney", url=pay_url))
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=markup)
    elif method == "stars":
        
        prices = [LabeledPrice(label="⭐ Донат", amount=amount)]
        bot.send_invoice(
            chat_id=chat_id,
            title="Поддержка канала",
            description=f"Пожертвование {amount}₽ через Telegram Stars",
            provider_token=TELEGRAM_PAYMENT_PROVIDER_TOKEN,
            currency="XTR",
            prices=prices,
            start_parameter="donate_stars",
            invoice_payload="donate_stars_payload"
        )
    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def handle_successful_payment(message):
    amount = message.successful_payment.total_amount / 100
    donation = {
        "chat_id": message.chat.id,
        "amount": int(amount),
        "username": message.from_user.first_name,
        "method": "Telegram Stars"
        
    }
    complete_donation(bot, donation)


def periodic_check():
    remove_crypto = []
    for invoice_id, donation in pending_cryptobot.items():
        status = check_cryptobot_payment_status(invoice_id)
        if status == "paid":
            complete_donation(bot, donation)
            remove_crypto.append(invoice_id)
    for invoice_id in remove_crypto:
        del pending_cryptobot[invoice_id]
    remove_yoomoney = []
    for label, donation in pending_yoomoney.items():
        status = check_yoomoney_payment_status(label)
        if status == "success":
            complete_donation(bot, donation)
            remove_yoomoney.append(label)
    for label in remove_yoomoney:
        del pending_yoomoney[label]
    threading.Timer(10, periodic_check).start()

if __name__ == "__main__":
    periodic_check()
    bot.polling(none_stop=True)