from config import CHANNEL_LINK, BOT_LINK
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random
import database
from datetime import datetime

THANK_YOU_PHRASES = [
    "🙏 Спасибо за вашу щедрость! Вы делаете мир лучше! ❤️",
    "🌟 Огромное спасибо за поддержку! Вы — настоящий герой! 💫",
    "💖 Благодарим за вклад! Без вас мы бы не справились! ✨",
    "🫶 Ваша помощь бесценна! Спасибо за доверие! 🌈",
    "🔥 Вы зажигаете сердца своим примером! Спасибо! 🚀",
    "🌻 Спасибо за доброе сердце и щедрость! Пусть добро вернётся! 💐",
    "🤝 Ваш вклад помогает нам расти! Искренне благодарим! 🌱",
    "💫 Спасибо за веру в нас! Вы вдохновляете! ✨",
    "🌍 Благодаря вам мы меняем мир к лучшему! Спасибо! 🌟",
    "🕊️ Мир становится добрее благодаря таким людям, как вы! Благодарим! ❤️"
]

def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

def complete_donation(bot, donation):
    chat_id = donation["chat_id"]
    amount = escape_markdown(donation["amount"])
    method = escape_markdown(donation["method"])
    
    # Определяем отображаемую валюту
    currency = "⭐" if method == "Telegram Stars" else "₽"
    amount_display = f"{amount}{currency}"
    
    username = escape_markdown(donation["username"])
    thank_you_message = escape_markdown(random.choice(THANK_YOU_PHRASES))
    
    if BOT_LINK.startswith("@"):
        bot_url = f"https://t.me/{BOT_LINK[1:]}"
    else:
        bot_url = BOT_LINK

    channel_msg = fr"""
🎉 *{username}* внесла пожертвование в размере *{amount_display}*
🔸 *Метод:* _{method}_

{thank_you_message}

🚀 Разработано [worpli](https://t.me/worpli)
💸 [Закинуть донат]({bot_url}) 👇
    """.strip()

    channel_message = bot.send_message(
        CHANNEL_LINK,
        channel_msg,
        parse_mode='MarkdownV2',
        disable_web_page_preview=True
    )
    
    if CHANNEL_LINK.startswith("@"):
        message_link = f"https://t.me/{CHANNEL_LINK[1:]}/{channel_message.message_id}"
    else:
        message_link = f"{CHANNEL_LINK}/{channel_message.message_id}"
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🌐 Посмотреть донат", url=message_link),
        InlineKeyboardButton("💸 Новый донат", url=bot_url)
    )
    
    user_msg = fr"""
✅ *Платеж успешно завершен\!*

▫️ *Сумма:* {amount}{currency}
▫️ *Метод оплаты:* {method}

✨ Ваша поддержка помогает нам развиваться\! 
🔄 Вы можете проверить статус или сделать новый донат:
    """.strip()

    if "message_id" in donation:
        bot.edit_message_text(
            text=user_msg,
            chat_id=chat_id,
            message_id=donation["message_id"],
            reply_markup=markup,
            parse_mode='MarkdownV2'
        )
    else:
        bot.send_message(
            chat_id,
            user_msg,
            reply_markup=markup,
            parse_mode='MarkdownV2'
        )
    
    full_name = donation.get("full_name", "").strip()
    if not full_name:
        full_name = "Не указано"
    
    donation_record = {
        "full_name": full_name,
        "username": donation.get("username", "—").strip(),
        "amount": int(donation["amount"]),
        "method": donation["method"],
        "donation_time": datetime.now()
    }
    database.add_donation(donation_record)