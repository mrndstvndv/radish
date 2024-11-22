import sqlite3

from tkcalendar.calendar_ import re

DATABASE = "school.db"


def create_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                date TEXT NOT NULL,
                subject TEXT NOT NULL,
                start_hour TEXT NOT NULL,
                start_minute TEXT NOT NULL,
                start_period TEXT NOT NULL,
                end_hour TEXT NOT NULL,
                end_minute TEXT NOT NULL,
                end_period TEXT NOT NULL,
                class_name TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                name TEXT PRIMARY KEY,
                coordinates TEXT NOT NULL
            )
        """)
        conn.commit()
    insert_rooms()  # Call insert_rooms to populate the rooms table


def create_table():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS example_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        conn.commit()


def insert_teacher(id, name):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO teachers (id, name) VALUES (?, ?)", (id, name)
        )
        conn.commit()


def insert_teacher_id(id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO teachers (id, name) VALUES (?, "")', (id,)
        )
        conn.commit()


def get_teacher_ids():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teachers")
        ids = [row[0] for row in cursor.fetchall()]
    return ids


def get_teacher_name(teacher_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,))
        row = cursor.fetchone()
        if row:
            return row["name"]
        return None


def get_subjects(teacher_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject_name FROM subjects WHERE teacher_id = ?", (teacher_id,)
        )
        subjects = [row["subject_name"] for row in cursor.fetchall()]
    return subjects


def insert_schedule(
    room,
    date,
    subject,
    start_hour,
    start_minute,
    start_period,
    end_hour,
    end_minute,
    end_period,
    class_name,
    teacher_id,
):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()

            # Check if the teacher_id exists in the teachers table
            cursor.execute("SELECT id FROM teachers WHERE id = ?", (teacher_id,))
            if cursor.fetchone() is None:
                raise ValueError(
                    f"Teacher ID {teacher_id} does not exist in the teachers table."
                )

            cursor.execute(
                """
                INSERT INTO schedule (room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, teacher_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    room,
                    date,
                    subject,
                    start_hour,
                    start_minute,
                    start_period,
                    end_hour,
                    end_minute,
                    end_period,
                    class_name,
                    teacher_id,
                ),
            )
            conn.commit()
            print(
                f"Schedule inserted successfully: {room}, {date}, {subject}, {start_hour}, {start_minute}, {start_period}, {end_hour}, {end_minute}, {end_period}, {class_name}, {teacher_id}"
            )  # Debugging
    except Exception as e:
        print(f"Error inserting schedule: {str(e)}")
        raise


def insert_rooms():
    rooms = {
        "CL-A": (200, 180, 370, 280),
        "CL-B": (370, 180, 540, 280),
        "CL-C": (540, 180, 710, 280),
        "CL-E": (255, 300, 425, 400),
        "CL-F": (425, 300, 655, 350),
        "CL-G": (425, 350, 655, 400),
        "L3": (370, 430, 450, 530),
        "L4": (450, 430, 530, 530),
        "CL-D": (530, 430, 710, 530),
        "L1": (60, 180, 140, 260),
        "L2": (60, 260, 140, 340),
    }

    with create_connection() as conn:
        cursor = conn.cursor()
        for name, coordinates in rooms.items():
            cursor.execute(
                "INSERT OR REPLACE INTO rooms (name, coordinates) VALUES (?, ?)",
                (name, str(coordinates)),
            )
        conn.commit()


def get_rooms():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM rooms")
        rooms = [row[0] for row in cursor.fetchall()]
    return rooms


def get_schedule():
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, s.room, s.date, s.subject, s.start_hour, s.start_minute, s.start_period, s.end_hour, s.end_minute, s.end_period, s.class_name, s.teacher_id, t.name as teacher_name
                FROM schedule s
                JOIN teachers t ON s.teacher_id = t.id
            """)
            schedule = cursor.fetchall()
            schedule_list = [dict(row) for row in schedule]
    except Exception as e:
        print(f"An error occurred: {e}")
        schedule_list = []
    return schedule_list


def get_schedule_by_id(schedule_id):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT s.id, s.room, s.date, s.subject, s.start_hour, s.start_minute, s.start_period, s.end_hour, s.end_minute, s.end_period, s.class_name, s.teacher_id, t.name as teacher_name
                FROM schedule s
                JOIN teachers t ON s.teacher_id = t.id
                WHERE s.id = ?
            """,
                (schedule_id,),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def update_schedule(updated_values):
    with create_connection() as conn:
        cursor = conn.cursor()

        set_clause = ",\n".join(
            [
                f"{k} = '{v}'"
                for k, v in updated_values.items()
                if k != "teacher_name" and k != "id"
            ]
        )

        query = f"""
            UPDATE schedule
            SET {set_clause}
            WHERE id = {updated_values["id"]};
        """

        print(query)

        cursor.execute(query)

        conn.commit()


def delete_schedule(room, date, start_hour, start_minute, start_period):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM schedule WHERE room = ? AND date = ? AND start_hour = ? AND start_minute = ? AND start_period = ?",
            (room, date, start_hour, start_minute, start_period),
        )
        conn.commit()


# Initialize the database (create tables if they do not exist)
initialize_database()

