import sqlite3


class SQLiteDatabaseConnection:
    def __init__(self, database_name: str):
        self.database_name = database_name
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()

            query = """
                CREATE TABLE IF NOT EXISTS week(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                day_of_week VARCHAR(20) NOT NULL
                )
            """
            cursor.execute(query)

            query = """
                CREATE TABLE IF NOT EXISTS schedule(
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    day_of_week VARCHAR(20) NOT NULL,
                    number_of_lesson INTEGER NOT NULL,
                    start_time VARCHAR(10) NOT NULL,
                    end_time VARCHAR(10) NOT NULL,
                    name_of_lesson TEXT NOT NULL,
                    FOREIGN KEY (day_of_week) REFERENCES week(day_of_week) 
                )             
            """
            cursor.execute(query)
            connection.commit()

    def get_record(self, day: str = ''):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()

            query = """
                SELECT schedule.number_of_lesson, schedule.start_time, schedule.end_time, schedule.name_of_lesson FROM schedule
                INNER JOIN week ON week.day_of_week = schedule.day_of_week
                WHERE week.day_of_week LIKE :day
            """
            result = cursor.execute(query, {"day": day}).fetchall()
            return result

    def edit_record(self, *, day: str, lesson: int, name_of_lesson: str):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()

            query = """
                UPDATE schedule
                SET name_of_lesson = :name_of_lesson
                WHERE schedule.day_of_week = :day AND schedule.number_of_lesson = :lesson
            """
            cursor.execute(query, {"day": day, "lesson": lesson, "name_of_lesson": name_of_lesson})

    def add_record(self, *, day: str, lesson: int, name_of_lesson: str):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            values = [day, lesson, TEMP_TIME_LIST[0], TEMP_TIME_LIST[1], name_of_lesson]
            query = """
                INSERT INTO schedule(day_of_week, number_of_lesson, start_time, end_time, name_of_lesson)
                VALUES (?,?,?,?,?)
            """
            cursor.execute(query, values)
            connection.commit()

    def delete_record(self, *, day: str, lesson: int):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = """
                DELETE FROM schedule
                WHERE day_of_week = :day AND number_of_lesson = :lesson
            """
            cursor.execute(query, {"day": day, "lesson": lesson})
            connection.commit()


week_days = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
}

schedule = {
    0: {
        1: '8:55-9:40   Навчаємось разом',
        2: '9:50-10:35  Українська література',
        4: '12:00-12:45 Фізика',
    },
    1: {
        1: '8:55-9:40   Алгебра',
        2: '9:50-10:35  Геометрія',
        4: '12:00-12:45 Англійська',
    }
}

ADMIN_ID = (5282220678, 5659473480)
CHAT_ID = ''
SYSTEM_BUTTONS = []
TEMP_DAY = ''
TEMP_TIME_LIST = []
TEMP_LESSONS_FOR_DAY = []
TEMP_LESSONS_NUMBERS = {
    '1': '8:55-9:40',
    '2': '9:50-10:35',
    '4': '12:00-12:45',
    '5': '13:00-13:45',
    '6': '13:55-14:40',
    '7': '14:50-15:35',
    '8': '15:45-16:30'
}
TEMP_LESSON_NUMBER = None
TEMP_LESSON_TITLE = ''

database = SQLiteDatabaseConnection('schedule_school.sqlite3')
