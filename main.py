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
    # if message.text == 'Back':
    #     return start(message)
    if message.text == 'Back':
        message.text = 'Choose day'
        return handle_messages(message)
    # elif message.text == 'Edit':
    #     bot.send_message(
    #         message.chat.id,
    #         'Choose lesson you want to edit...',
    #         parse_mode="Markdown",
    #         reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY)
    #     )
    #     bot.register_next_step_handler(message, edit_single_lesson)
    else:
        result_for_day = get_lessons_from_db(request_day=message.text)
        storage.TEMP_DAY = message.text
        bot.send_message(
            message.chat.id,
            result_for_day,
            parse_mode="Markdown",
            reply_markup=keyboards.day_actions_menu()
        )
        bot.register_next_step_handler(message, choose_day_option)


def choose_day_option(message):
    if message.text == 'Back':
        message.text = 'Choose day'
        return handle_messages(message)
    elif message.chat.id != storage.ADMIN_ID:
        message.text = storage.TEMP_DAY
        bot.send_message(message.chat.id, 'You are not authorised to do this action!', parse_mode="Markdown")
        return get_messages_for_day(message)
    try:
        current_keyboard_function = keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY) \
            if message.text == 'Edit' else keyboards.add_lesson_record()
        day_option_string = message.text + '_single_lesson'
        day_option_function = globals()[day_option_string.lower()]
        current_message = 'Please enter valid (free) number of lesson:' \
            if message.text == 'Add' else 'Please choose lesson to edit:'
        bot.send_message(
            message.chat.id,
            current_message,
            parse_mode="Markdown",
            reply_markup=current_keyboard_function,
        )
        bot.register_next_step_handler(message, day_option_function)
    except Exception as e:
        bot.send_message(message.chat.id, str(e))


def add_single_lesson(message):
    if message.text == 'Back':
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)
    lessons_at_the_day = [element[:1] for element in storage.TEMP_LESSONS_FOR_DAY]
    if message.text not in lessons_at_the_day and message.text in storage.TEMP_LESSONS_NUMBERS:
        storage.TEMP_TIME_LIST = storage.TEMP_LESSONS_NUMBERS[message.text].split('-')
        storage.TEMP_LESSON_NUMBER = int(message.text)
        bot.send_message(
            message.chat.id,
            f"Please enter lesson title for date:{storage.TEMP_DAY} and time: {storage.TEMP_TIME_LIST[0]}-{storage.TEMP_TIME_LIST[1]}",
            parse_mode="Markdown",
        )
        bot.register_next_step_handler(message, add_single_lesson_insert_to_db)
    elif message.text in lessons_at_the_day:
        bot.send_message(message.chat.id, 'Number is already in DB, try Edit feature...')
        bot.register_next_step_handler(message, add_single_lesson)
    else:
        bot.send_message(message.chat.id, 'Incorrect value, try again')
        bot.register_next_step_handler(message, add_single_lesson)


def add_single_lesson_insert_to_db(message):
    if message.text == "Back":
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)
    db.add_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER, name_of_lesson=message.text)
    get_lessons_from_db(request_day=storage.TEMP_DAY)
    bot.send_message(
        message.chat.id,
        'Saved to DB',
        reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY)
    )
    bot.register_next_step_handler(message, get_messages_for_day)


def edit_single_lesson(message):
    if message.text == 'Back':
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)
    elif storage.TEMP_LESSON_NUMBER:
        if message.text == 'Delete':
            message.text = storage.TEMP_DAY
            db.delete_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER)
            get_lessons_from_db(request_day=storage.TEMP_DAY)
            return get_messages_for_day(message)
        db.edit_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER, name_of_lesson=message.text)
        get_lessons_from_db(request_day=storage.TEMP_DAY)
        bot.send_message(
            message.chat.id,
            'Data saved to db',
            parse_mode="Markdown",
            reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY)
        )
        bot.register_next_step_handler(message, get_messages_for_day)
    elif message.text[:1] in storage.TEMP_LESSONS_NUMBERS:
        storage.TEMP_LESSON_NUMBER = int(message.text[:1])
        bot.send_message(
            message.chat.id,
            'Enter lesson title for this time:',
            parse_mode="Markdown",
            reply_markup=keyboards.get_edit_lesson_record()
        )
        bot.register_next_step_handler(message, edit_single_lesson)
    # else:
    #     bot.register_next_step_handler(message, edit_single_lesson)


@bot.message_handler(commands=['start'])
def start(message):
    print(f"Start chat with user: {message.from_user.id} - {message.from_user.first_name}")
    bot.send_message(
        message.chat.id,
        f"Welcome back, {message.from_user.first_name}",
        reply_markup=keyboards.get_keyboard()
    )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # chat_id = message.chat.id

    if message.text == 'Choose day':
        bot.send_message(
            message.chat.id,
            'Choose day to view schedule',
            reply_markup=keyboards.get_days_keyboard()
        )
        bot.register_next_step_handler(message, get_messages_for_day)
    elif message.text == 'Today Tasks':
        bot.send_message(message.chat.id, get_lessons_from_db())
    elif message.text == 'Start':
        start(message)
    else:
        bot.send_message(
            message.chat.id,
            'Please choose element in bottom menu ',
            reply_markup=keyboards.get_keyboard()
        )


if __name__ == '__main__':
    bot.infinity_polling()
