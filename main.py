import config
import telebot
from datetime import datetime
import storage
import logging
import keyboards
from tools import get_messages

bot = telebot.TeleBot(config.TOKEN)


def get_messages_for_day(message):
    if message.text == 'Back to start':
        return start(message)
    result_for_day = get_messages(message, request_day=message.text)
    bot.send_message(storage.CHAT_ID, result_for_day, parse_mode="Markdown", reply_markup=keyboards.get_days_keyboard())
    bot.register_next_step_handler(message, get_messages_for_day)


@bot.message_handler(commands=['start'])
def start(message):
    storage.CHAT_ID = message.chat.id
    print(f"{message.text} - {message.from_user.first_name}")
    bot.send_message(
        storage.CHAT_ID,
        f"Welcome back, {message.from_user.first_name}",
        reply_markup=keyboards.get_keyboard()
    )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # chat_id = message.chat.id

    if message.text == 'Choose day':
        bot.send_message(storage.CHAT_ID, 'Choose day to view schedule', reply_markup=keyboards.get_days_keyboard())
        bot.register_next_step_handler(message, get_messages_for_day)
    elif message.text == 'Today Tasks':
        bot.send_message(storage.CHAT_ID, get_messages(message))
    elif message.text == 'Start':
        start(message)
    else:
        bot.send_message(storage.CHAT_ID, 'Please choose element in bottom menu ',
                         reply_markup=keyboards.get_keyboard())


if __name__ == '__main__':
    bot.infinity_polling()
