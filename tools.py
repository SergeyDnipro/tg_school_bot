from datetime import datetime
import telebot
import storage


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

