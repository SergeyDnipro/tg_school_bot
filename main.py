import config
import telebot
from datetime import datetime
import storage
from storage import database as db
import logging
import keyboards
from tools import get_messages, get_lessons_from_db
from telebot import types


bot = telebot.TeleBot(config.TOKEN)


def get_messages_for_day(message):
    storage.TEMP_LESSON_NUMBER = None
    if message.text == 'Back':
        return start(message)
    if message.text == 'Back':
        message.text = 'Choose day'
        return handle_messages(message)
    elif message.text == 'Edit':
        bot.send_message(storage.CHAT_ID, 'Choose lesson you want to edit...', parse_mode="Markdown", reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY))
        bot.register_next_step_handler(message, edit_single_lesson)
    else:
        result_for_day = get_lessons_from_db(request_day=message.text)
        storage.TEMP_DAY = message.text
        bot.send_message(storage.CHAT_ID, result_for_day, parse_mode="Markdown", reply_markup=keyboards.day_actions_menu())
        bot.register_next_step_handler(message, choose_day_option)


def choose_day_option(message):
    if message.text == 'Back':
        message.text = 'Choose day'
        return handle_messages(message)
    try:
        day_option_string = message.text + '_single_lesson'
        day_option_funtion = globals()[day_option_string.lower()]
        bot.send_message(storage.CHAT_ID, 'Choose action you want - Add/Edit...', parse_mode="Markdown", reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY))
        bot.register_next_step_handler(message, day_option_funtion)
    except Exception as e:
        bot.send_message(storage.CHAT_ID, str(e))


def add_single_lesson(message):
    print('******')


def edit_single_lesson(message):
    if message.text == 'Back':
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)
    elif storage.TEMP_LESSON_NUMBER:
        db.edit_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER, name_of_lesson=message.text)
        get_lessons_from_db(request_day=storage.TEMP_DAY)
        bot.send_message(storage.CHAT_ID, 'Data saved to db', parse_mode="Markdown", reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY))
        bot.register_next_step_handler(message, get_messages_for_day)
    elif message.text[:1] in storage.TEMP_LESSONS_NUMBERS:
        storage.TEMP_LESSON_NUMBER = int(message.text[:1])
        bot.send_message(storage.CHAT_ID, 'Enter lesson title for this time:', parse_mode="Markdown",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, edit_single_lesson)
    # else:
    #     bot.register_next_step_handler(message, edit_single_lesson)


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
        bot.send_message(storage.CHAT_ID, get_lessons_from_db())
    elif message.text == 'Start':
        start(message)
    else:
        bot.send_message(storage.CHAT_ID, 'Please choose element in bottom menu ',
                         reply_markup=keyboards.get_keyboard())


if __name__ == '__main__':
    bot.infinity_polling()
