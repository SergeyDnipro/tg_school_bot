import config
from telebot import types
from storage import SYSTEM_BUTTONS
from storage import database as db


def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_choice_day = types.KeyboardButton(text=config.DAY_CHOICE_BUTTON)
    button_get_tasks = types.KeyboardButton(text=config.TODAY_SCHEDULE_BUTTON)
    # button_start = types.KeyboardButton(text="Start")
    keyboard.add(button_choice_day, button_get_tasks)
    button_week_schedule = types.KeyboardButton(text=config.WEEK_SCHEDULE_BUTTON)
    keyboard.add(button_week_schedule)
    list_of_buttons = [button_choice_day.text, button_get_tasks.text, button_week_schedule.text]
    SYSTEM_BUTTONS.extend(list_of_buttons) if not SYSTEM_BUTTONS else None
    return keyboard


def get_days_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    monday = types.KeyboardButton(text=config.MONDAY_BUTTON)
    tuesday = types.KeyboardButton(text=config.TUESDAY_BUTTON)
    wednesday = types.KeyboardButton(text=config.WEDNESDAY_BUTTON)
    thursday = types.KeyboardButton(text=config.THURSDAY_BUTTON)
    friday = types.KeyboardButton(text=config.FRIDAY_BUTTON)

    keyboard.add(monday, tuesday, wednesday, thursday, friday)
    back_button = types.KeyboardButton(text=config.BACK_BUTTON)
    keyboard.add(back_button)
    return keyboard


def day_actions_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    add_button = types.KeyboardButton(text=config.ADD_LESSON_BUTTON)
    edit_button = types.KeyboardButton(text=config.EDIT_LESSON_BUTTON)
    keyboard.add(add_button, edit_button)
    back_button = types.KeyboardButton(text=config.BACK_BUTTON)
    keyboard.add(back_button)
    return keyboard


def get_lessons_keyboard(lessons: str):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    lesson_temp = []
    for lesson in lessons:
        lesson_button = types.KeyboardButton(text=lesson)
        lesson_temp.append(lesson_button)
    keyboard.add(*lesson_temp)

    back_button = types.KeyboardButton(text=config.BACK_BUTTON)
    keyboard.add(back_button)
    return keyboard


def get_edit_lesson_record():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    delete_button = types.KeyboardButton(text=config.DELETE_LESSON_BUTTON)
    back_button = types.KeyboardButton(text=config.BACK_BUTTON)
    keyboard.add(back_button, delete_button)
    return keyboard


def add_lesson_record():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    back_button = types.KeyboardButton(text=config.BACK_BUTTON)
    keyboard.add(back_button)
    return keyboard
