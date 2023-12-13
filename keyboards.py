from telebot import types
from storage import SYSTEM_BUTTONS


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
    back_button = types.KeyboardButton(text="Back to start")
    keyboard.add(back_button)
    return keyboard

