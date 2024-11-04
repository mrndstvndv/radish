from database import insert_schedule, create_connection, create_table, insert_teacher, insert_rooms, get_schedule

def all_schedules():
    # Initialize the database and tables
    create_table()

    # Add sample teacher
    insert_teacher("21-24870", "John Doniego")

    # Insert room data
    insert_rooms()

    # Fetch and print all schedules
    schedules = get_schedule()
    for schedule in schedules:
        print(schedule)

# Debugging: Print all schedules to verify insertion
def print_all_schedules():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM schedule')
    rows = cursor.fetchall()
    for row in rows:
        print(dict(row))
    conn.close()

# Call this function to verify data insertion
all_schedules()
print_all_schedules()