from config import CHANNEL_LINK
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def complete_donation(bot, donation):
    chat_id = donation["chat_id"]
    amount = donation["amount"]
    method = donation["method"]
    username = donation["username"]

    
    if CHANNEL_LINK.startswith("@"):
        channel_username = CHANNEL_LINK[1:]  
        channel_url = f"https://t.me/{channel_username}"
    else:
        channel_username = None
        channel_url = CHANNEL_LINK

    
    channel_message = bot.send_message(
        CHANNEL_LINK,
        f"✨ {username} пожертвовал {amount}₽ через {method}! Спасибо за поддержку! ❤️ Бот создал https://t.me/worpli"
    )

    
    if channel_username:
        message_link = f"https://t.me/{channel_username}/{channel_message.message_id}"
    else:
        message_link = channel_url  

    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 Перейти к донату", url=message_link))

    
    if "message_id" in donation:
        bot.edit_message_text(
            text=f"🎉 Вы оплатили {amount}₽ через {method}! Спасибо Вам большое! 🙏\nВаш донат будет виден здесь:",
            chat_id=chat_id,
            message_id=donation["message_id"],
            reply_markup=markup
        )
    else:
        
        bot.send_message(
            chat_id,
            f"🎉 Вы оплатили {amount}₽ через {method}! Спасибо Вам большое! 🙏\nВаш донат будет виден здесь: {message_link}"
        )