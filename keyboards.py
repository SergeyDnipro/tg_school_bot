from telebot import types
from storage import SYSTEM_BUTTONS
from storage import database as db


def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_choice_day = types.KeyboardButton(text="Choose day")
    button_get_tasks = types.KeyboardButton(text="Today Tasks")
    button_start = types.KeyboardButton(text="Start")
    keyboard.add(button_choice_day, button_get_tasks, button_start)
    list_of_buttons = [button_choice_day.text, button_get_tasks.text, button_start.text]
    SYSTEM_BUTTONS.extend(list_of_buttons) if not SYSTEM_BUTTONS else None
    print(SYSTEM_BUTTONS)
    return keyboard


def get_days_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    monday = types.KeyboardButton(text="Monday")
    tuesday = types.KeyboardButton(text="Tuesday")
    wednesday = types.KeyboardButton(text="Wednesday")
    thursday = types.KeyboardButton(text="Thursday")
    friday = types.KeyboardButton(text="Friday")

    keyboard.add(monday, tuesday, wednesday, thursday, friday)
    back_button = types.KeyboardButton(text="Back")
    keyboard.add(back_button)
    return keyboard


def day_actions_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    add_button = types.KeyboardButton(text="Add")
    edit_button = types.KeyboardButton(text="Edit")
    keyboard.add(add_button, edit_button)
    back_button = types.KeyboardButton(text="Back")
    keyboard.add(back_button)
    return keyboard


def get_lessons_keyboard(lessons: str):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    lesson_temp = []
    for lesson in lessons:
        lesson_button = types.KeyboardButton(text=lesson)
        lesson_temp.append(lesson_button)
    keyboard.add(*lesson_temp)

    back_button = types.KeyboardButton('Back')
    keyboard.add(back_button)
    return keyboard


def get_edit_lesson_record():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    delete_button = types.KeyboardButton('Delete')
    back_button = types.KeyboardButton('Back')
    keyboard.add(back_button, delete_button)
    return keyboard
