import config
import telebot, schedule, time, datetime, threading, os
import storage
import keyboards
import redis
import json
from storage import database as db
from tools import get_schedule_for_day_from_db, get_schedule_for_week_from_db, get_schedule_from_cache_or_set
from logger import main_logger
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(',')))
bot = telebot.TeleBot(TOKEN)
redis_instance = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)


def run_scheduler():
    get_schedule_from_cache_or_set(redis_instance=redis_instance, refresh=True)
    while True:
        schedule.run_pending()
        time.sleep(1)


def check_db_and_send_message_to_tg():
    users_dict = redis_instance.hgetall('subscribers')
    response = get_schedule_from_cache_or_set(redis_instance)

    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.today().strftime("%A")

    for lesson_data in response:
        start_time_lesson = lesson_data[1]
        start_time_lesson_alert_dt_obj = datetime.datetime.strptime(start_time_lesson, "%H:%M") - datetime.timedelta(seconds=120)
        start_time_lesson_alert_time_obj = start_time_lesson_alert_dt_obj.time()
        db_day = lesson_data[4]

        end_time_lesson_alert_time_obj = (start_time_lesson_alert_dt_obj + datetime.timedelta(seconds=70)).time()

        if (current_day == db_day
                and start_time_lesson_alert_time_obj < current_time <end_time_lesson_alert_time_obj)\
                and not lesson_data[3].strip().startswith("-"):
            alert_msg = f"<u>Нагадування.</u>\n\nУрок '{lesson_data[3]}' починається о: {lesson_data[1]}.\nНе запізнюйтесь."
            for user_id, user_name in users_dict.items():
                bot.send_message(int(user_id), alert_msg, parse_mode="HTML")
                main_logger.info(
                    f"Sending notification to {int(user_id)} ({user_name}). "
                    f"Lesson: {lesson_data[3]}, starts in: {lesson_data[1]}"
                )


def get_messages_for_day(message):
    storage.TEMP_LESSON_NUMBER = None

    if message.text == config.BACK_BUTTON:
        return start(message)

    else:
        result_for_day = get_schedule_for_day_from_db(request_day=storage.days_dict[message.text])
        storage.TEMP_DAY = storage.days_dict[message.text]
        bot.send_message(
            message.chat.id,
            result_for_day,
            parse_mode="HTML",
            reply_markup=keyboards.day_actions_menu()
        )
        # Request for day logging
        main_logger.info(f"User {message.from_user.first_name} ({message.from_user.id}) request schedule for {message.text}")
        bot.register_next_step_handler(message, choose_day_option)
        return None


def choose_day_option(message):

    if message.text == config.BACK_BUTTON:
        message.text = config.DAY_CHOICE_BUTTON
        return handle_messages(message)
    elif message.chat.id not in ADMIN_IDS:
        message.text = storage.TEMP_DAY
        bot.send_message(message.chat.id, 'You are not authorised to perform this action!', parse_mode="HTML")
        # Try to edit/delete without authorization logging
        main_logger.warning(f"User {message.from_user.first_name} ({message.from_user.id}) try to add/edit/delete schedule record")
        return get_messages_for_day(message)

    try:
        if message.text == config.ADD_LESSON_BUTTON:
            current_keyboard_function = keyboards.add_lesson_record()
            day_option_function = add_single_lesson
            current_message = "Введіть номер уроку, що ви бажаєте додати: "

        elif message.text == config.EDIT_LESSON_BUTTON:
            current_keyboard_function = keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY)
            day_option_function = edit_single_lesson
            current_message = "Виберіть урок для редагування:"

        else:
            current_message = "Not valid command, try again"
            current_keyboard_function = keyboards.day_actions_menu()
            day_option_function = choose_day_option

        bot.send_message(
            message.chat.id,
            current_message,
            parse_mode="HTML",
            reply_markup=current_keyboard_function,
        )

        bot.register_next_step_handler(message, day_option_function)
        return None

    except Exception as e:
        bot.send_message(message.chat.id, str(e))
        return None


def add_single_lesson(message):
    if message.text == config.BACK_BUTTON:
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)
    lessons_at_the_day = [element[:1] for element in storage.TEMP_LESSONS_FOR_DAY]

    if message.text not in lessons_at_the_day and message.text in storage.TEMP_LESSONS_NUMBERS:
        storage.TEMP_TIME_LIST = storage.TEMP_LESSONS_NUMBERS[message.text].split('-')
        storage.TEMP_LESSON_NUMBER = int(message.text)
        bot.send_message(
            message.chat.id,
            f"Введіть нову назву {storage.TEMP_LESSON_NUMBER}-го уроку в {storage.days_dict_eng_ukr[storage.TEMP_DAY]}, "
            f" або '-' (якщо уроку немає): ",
            parse_mode="HTML",
        )
        bot.register_next_step_handler(message, add_single_lesson_insert_to_db)
        return None

    elif message.text in lessons_at_the_day:
        bot.send_message(message.chat.id, 'Number is already in DB, try another number...')
        bot.register_next_step_handler(message, add_single_lesson)
        return None

    else:
        bot.send_message(message.chat.id, 'Incorrect value, try again')
        bot.register_next_step_handler(message, add_single_lesson)
        return None


def add_single_lesson_insert_to_db(message):
    if message.text == config.BACK_BUTTON:
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)
    msg_lesson_title = config.NO_LESSON if message.text == '-' else message.text
    db.add_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER, name_of_lesson=msg_lesson_title)

    # Refresh cache after changing DB
    get_schedule_from_cache_or_set(redis_instance=redis_instance, refresh=True)

    # Add record logging
    main_logger.warning(f"User {message.from_user.first_name} ({message.from_user.id}) "
                        f"added record for {storage.TEMP_DAY}, Lesson {storage.TEMP_LESSON_NUMBER} - {message.text}")
    get_schedule_for_day_from_db(request_day=storage.TEMP_DAY)

    bot.send_message(
        message.chat.id,
        "Дані збережено... ",
    )
    message.text = storage.TEMP_DAY
    return get_messages_for_day(message)


def edit_single_lesson(message):
    if message.text == config.BACK_BUTTON:
        message.text = storage.TEMP_DAY
        return get_messages_for_day(message)

    elif storage.TEMP_LESSON_NUMBER:
        if message.text == config.DELETE_LESSON_BUTTON:
            message.text = storage.TEMP_DAY
            db.delete_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER)

            # Refresh cache after changing DB
            get_schedule_from_cache_or_set(redis_instance=redis_instance, refresh=True)

            # Delete-record logger
            main_logger.warning(f"User {message.from_user.first_name} ({message.from_user.id}) "
                                f"delete record for: {storage.TEMP_DAY}, Lesson {storage.TEMP_LESSON_NUMBER}")
            get_schedule_for_day_from_db(request_day=storage.TEMP_DAY)
            return get_messages_for_day(message)

        msg_lesson_title = config.NO_LESSON if message.text == '-' else message.text
        db.edit_record(day=storage.TEMP_DAY, lesson=storage.TEMP_LESSON_NUMBER, name_of_lesson=msg_lesson_title)

        # Refresh cache after changing DB
        get_schedule_from_cache_or_set(redis_instance=redis_instance, refresh=True)

        # Edit-record logger
        main_logger.warning(f"User {message.from_user.first_name} ({message.from_user.id}) "
                            f"edited record for {storage.TEMP_DAY}, Lesson {storage.TEMP_LESSON_NUMBER} - {message.text}")

        # Get a new lesson list for keyboard
        get_schedule_for_day_from_db(request_day=storage.TEMP_DAY)

        bot.send_message(
            message.chat.id,
            "Дані збережено... ",
            parse_mode="HTML",
            reply_markup=keyboards.get_lessons_keyboard(storage.TEMP_LESSONS_FOR_DAY)
        )

        storage.TEMP_LESSON_NUMBER = None
        bot.register_next_step_handler(message, edit_single_lesson)
        return None

    elif message.text[:1] in storage.TEMP_LESSONS_NUMBERS:
        storage.TEMP_LESSON_NUMBER = int(message.text[:1])
        bot.send_message(
            message.chat.id,
            f"Введіть нову назву {storage.TEMP_LESSON_NUMBER}-го уроку в {storage.days_dict_eng_ukr[storage.TEMP_DAY]}, "
            f" або '-' (якщо уроку немає): ",
            parse_mode="Markdown",
            reply_markup=keyboards.get_edit_lesson_record()
        )
        bot.register_next_step_handler(message, edit_single_lesson)
        return None
    return None


@bot.message_handler(commands=['start'])
def start(message):
    # New user start logging
    main_logger.info(f"Start chat with user: {message.from_user.first_name} ({message.from_user.id})")

    bot.send_message(
        message.chat.id,
        f"Welcome back, {message.from_user.first_name}",
        reply_markup=keyboards.get_keyboard(redis_instance=redis_instance, message=message)
    )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):

    if message.text == config.DAY_CHOICE_BUTTON:
        bot.send_message(
            message.chat.id,
            "Виберіть день, щоб побачити розклад",
            reply_markup=keyboards.get_days_keyboard()
        )
        bot.register_next_step_handler(message, get_messages_for_day)

    elif message.text == config.TODAY_SCHEDULE_BUTTON:
        bot.send_message(message.chat.id, get_schedule_for_day_from_db(), parse_mode="HTML")
        # Today request logging
        main_logger.info(f"User {message.from_user.first_name} ({message.from_user.id}) request schedule for today")

    elif message.text == config.WEEK_SCHEDULE_BUTTON:
        bot.send_message(message.chat.id, get_schedule_for_week_from_db(), parse_mode='HTML')
        # Week request logging
        main_logger.info(f"User {message.from_user.first_name} ({message.from_user.id}) request schedule for week")
    else:
        if message.text == config.SUBSCRIBE_BUTTON:
            message_for_chat = 'Subscribed'
            redis_instance.hset('subscribers', message.from_user.id, message.from_user.first_name)
            main_logger.info(f"User {message.from_user.first_name} ({message.from_user.id}) turned ON lessons notification")
        elif message.text == config.UNSUBSCRIBE_BUTTON:
            message_for_chat = 'Unsubscribed'
            redis_instance.hdel('subscribers', message.from_user.id)
            main_logger.warning(f"User {message.from_user.first_name} ({message.from_user.id}) turned OFF lessons notification")
        else:
            message_for_chat = "Будь ласка, виберіть елемент із нижнього меню"

        bot.send_message(
            message.chat.id,
            message_for_chat,
            reply_markup=keyboards.get_keyboard(redis_instance=redis_instance, message=message),
            parse_mode="HTML"
        )

threading.Thread(target=run_scheduler, daemon=True).start()
schedule.every(1).minutes.do(check_db_and_send_message_to_tg)

if __name__ == '__main__':
    bot.infinity_polling()
