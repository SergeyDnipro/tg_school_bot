from datetime import datetime
import telebot
import storage
from storage import database as db
from logger import main_logger
import config


def serialize_tuple_to_dict(response: list):
    try:
        response.sort(key=lambda element: element[0])
        serialized_response = [
            dict(
                order_number=lesson[0],
                start_time=lesson[1],
                end_time=lesson[2],
                lesson_name=lesson[3],
                weekday=lesson[4]
            ) for lesson in response
        ]
    except (IndexError, TypeError) as e:
        main_logger.error(f"Error while sorting/serializing response from DB, {e}")
        return None
    return serialized_response


# def get_messages(message, request_day=None):
#     day = storage.week_days[request_day] if request_day else datetime.today().weekday()
#     if day in storage.schedule:
#         result_day = f"Сьогодні:: {datetime.now().strftime('%A, %d/%m/%y')}\n" if not request_day else f"Розклад на: {request_day}:\n"
#         for order, task in storage.schedule[day].items():
#             if order == 1:
#                 result_day += f"\nONLINE"
#             elif order == 4:
#                 result_day += f"\n\nOFFLINE"
#             result_day += f"\n{order} - {task}"
#         return result_day
#     else:
#         return 'No records'

def output_lessons_for_day(result_queryset: list, day: str) -> str:
    serialized_response = serialize_tuple_to_dict(result_queryset)
    online_flag = False
    offline_flag = False
    result_day_str = ''
    for element in serialized_response:
        if element['order_number'] < 6 and not online_flag:
            result_day_str += f"\n<b>ONLINE</b>"
            online_flag = True
        elif element['order_number'] >= 6 and not offline_flag:
            result_day_str += f"\n\n<b>OFFLINE</b>"
            offline_flag = True
        lesson_time = f"{element['start_time']}-{element['end_time']}"
        result_day_str += f"\n{element['order_number']}. {lesson_time}  - {element['lesson_name']}"
        if datetime.strptime(element['start_time'], '%H:%M').time() < datetime.now().time() < datetime.strptime(
                element['end_time'].strip(), '%H:%M').time() \
                and day == datetime.today().strftime('%A'):
            result_day_str += '- NOW'
        storage.TEMP_LESSONS_FOR_DAY.append(
            f"{element['order_number']}.\t   {element['start_time']}-{element['end_time']} - {element['lesson_name']}")

    return result_day_str


def get_schedule_for_week_from_db():
    response = db.get_all_records()

    if response:
        result_week_str = "Розклад на тиждень:\n"
        for day in config.WEEKDAYS:
            day_filtered_response = list(filter(lambda element: element[4] == storage.days_dict[day], response))
            if day_filtered_response:
                # result_week_str += "\n------------------------ "
                result_week_str += f"\n\n<u><b>{day}</b></u>\n"
                result_week_str += f"{output_lessons_for_day(day_filtered_response, day)}\n"

        return result_week_str
    else:
        return "No records found"



def get_schedule_for_day_from_db(request_day: str = None):
    day = request_day if request_day in storage.days_dict_eng_ukr else datetime.today().strftime('%A')

    storage.TEMP_LESSONS_FOR_DAY.clear()
    response = db.get_record(day)

    # response.sort(key=lambda x: x[0])

    if response:
        formatted_day = storage.days_dict_eng_ukr[day]
        formatted_date = datetime.now().strftime('%d/%m/%Y')
        result_day = f"Сьогодні: {formatted_day}, {formatted_date}\n" if not request_day else f"Розклад на: <u>{storage.days_dict_eng_ukr[day]}</u>\n"
        day_data_display = output_lessons_for_day(response, day)
        result_day += day_data_display
        # for element in serialized_response:
        #     if element['order_number'] < 6 and not online_flag:
        #         result_day += f"\nONLINE"
        #         online_flag = True
        #     elif element['order_number'] >= 6 and not offline_flag:
        #         result_day += f"\n\nOFFLINE"
        #         offline_flag = True
        #     result_day += f"\n{element['order_number']}. {element['start_time']}-{element['end_time']} - {element['lesson_name']}"
        #     if datetime.strptime(element['start_time'], '%H:%M').time() < datetime.now().time() < datetime.strptime(element['end_time'], '%H:%M').time()\
        #             and day == datetime.today().strftime('%A'):
        #         result_day += '- NOW'
        #     storage.TEMP_LESSONS_FOR_DAY.append(f"{element['order_number']}.\t   {element['start_time']}-{element['end_time']} - {element['lesson_name']}")
        return result_day
    else:
        return 'No records found'


def get_lesson_from_db(request_day: str, lesson_id):
    pass
