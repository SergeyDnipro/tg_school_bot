from datetime import datetime
import telebot
import storage
from storage import database as db


def serialize_tuple_to_dict(responce: list) -> list:
    serialized_response = [
        dict(
            order_number=lesson[0],
            start_time=lesson[1],
            end_time=lesson[2],
            lesson_name=lesson[3]
        ) for lesson in responce
    ]
    return serialized_response


def get_messages(message, request_day=None):
    print(request_day)
    day = storage.week_days[request_day] if request_day else datetime.today().weekday()
    if day in storage.schedule:
        result_day = f"Today is: {datetime.now().strftime('%A, %d/%m/%y')}\n" if not request_day else f"Schedule for {request_day}:\n"
        for order, task in storage.schedule[day].items():
            if order == 1:
                result_day += f"\nONLINE"
            elif order == 4:
                result_day += f"\n\nOFFLINE"
            result_day += f"\n{order} - {task}"
        return result_day
    else:
        return 'No records'


def get_lessons_from_db(request_day: str = None):
    day = request_day if request_day else datetime.today().strftime('%A')
    storage.TEMP_LESSONS_FOR_DAY.clear()
    responce = db.get_record(day)
    if responce:
        result_day = f"Today is: {datetime.now().strftime('%A, %d/%m/%y')}\n" if not request_day else f"Schedule for {request_day}:\n"
        serialized_response = serialize_tuple_to_dict(responce)
        for element in serialized_response:
            if element['order_number'] == 1:
                result_day += f"\nONLINE"
            elif element['order_number'] == 4:
                result_day += f"\n\nOFFLINE"
            result_day += f"\n{element['order_number']} - {element['start_time']}-{element['end_time']} - {element['lesson_name']}"
            if datetime.strptime(element['start_time'], '%H:%M').time() < datetime.now().time() < datetime.strptime(element['end_time'], '%H:%M').time():
                result_day += '- NOW'
            storage.TEMP_LESSONS_FOR_DAY.append(f"{element['order_number']}.\t   {element['start_time']}-{element['end_time']} - {element['lesson_name']}")
        return result_day
    else:
        return 'No records'


def get_lesson_from_db(request_day: str, lesson_id):
    pass
