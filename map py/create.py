import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from tkcalendar import DateEntry  # Import DateEntry from tkcalendar
import os
import sys
from database import insert_schedule, get_rooms
from datetime import date  # Import date from datetime

class SchedulerApp:
    def __init__(self, root, teacher_id):
        self.root = root
        self.teacher_id = teacher_id
        self.root.title("Create Schedule")

        # Create form elements
        self.create_form()

    def create_form(self):
        form_frame = tk.Frame(self.root)
        form_frame.pack(padx=10, pady=10)

        tk.Label(form_frame, text="Room:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.room_var = tk.StringVar()
        self.room_menu = ttk.Combobox(form_frame, textvariable=self.room_var, values=self.get_rooms())
        self.room_menu.grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Date:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.date_entry = DateEntry(form_frame, selectmode='day', mindate=date.today())
        self.date_entry.grid(row=1, column=1, pady=2)

        tk.Label(form_frame, text="Subject:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.subject_var = tk.StringVar()
        self.subject_menu = ttk.Combobox(form_frame, textvariable=self.subject_var, values=self.get_subjects())
        self.subject_menu.grid(row=2, column=1, pady=2)

        tk.Label(form_frame, text="Start Time:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.start_hour_var = tk.StringVar()
        self.start_minute_var = tk.StringVar()
        self.start_time_period = tk.StringVar()
        self.start_hour_menu = ttk.Combobox(form_frame, textvariable=self.start_hour_var, values=[str(i) for i in range(1, 13)])
        self.start_minute_menu = ttk.Combobox(form_frame, textvariable=self.start_minute_var, values=[str(i).zfill(2) for i in range(0, 60)])
        self.start_period_menu = ttk.Combobox(form_frame, textvariable=self.start_time_period, values=["AM", "PM"])
        self.start_hour_menu.grid(row=3, column=1, pady=2)
        self.start_minute_menu.grid(row=3, column=2, pady=2)
        self.start_period_menu.grid(row=3, column=3, pady=2)

        tk.Label(form_frame, text="End Time:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.end_hour_var = tk.StringVar()
        self.end_minute_var = tk.StringVar()
        self.end_time_period = tk.StringVar()
        self.end_hour_menu = ttk.Combobox(form_frame, textvariable=self.end_hour_var, values=[str(i) for i in range(1, 13)])
        self.end_minute_menu = ttk.Combobox(form_frame, textvariable=self.end_minute_var, values=[str(i).zfill(2) for i in range(0, 60)])
        self.end_period_menu = ttk.Combobox(form_frame, textvariable=self.end_time_period, values=["AM", "PM"])
        self.end_hour_menu.grid(row=4, column=1, pady=2)
        self.end_minute_menu.grid(row=4, column=2, pady=2)
        self.end_period_menu.grid(row=4, column=3, pady=2)

        tk.Label(form_frame, text="Class Name:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.class_name_var = tk.StringVar()
        self.class_name_entry = tk.Entry(form_frame, textvariable=self.class_name_var)
        self.class_name_entry.grid(row=5, column=1, pady=2)

        submit_button = tk.Button(form_frame, text="Submit", command=self.submit_schedule)
        submit_button.grid(row=6, column=0, columnspan=2, pady=10)

        back_button = tk.Button(form_frame, text="Back", command=self.go_back)
        back_button.grid(row=6, column=2, columnspan=2, pady=10)

    def get_subjects(self):
        # Placeholder for subjects, should be replaced with actual logic to fetch subjects
        return ["Math", "Science", "History"]

    def get_rooms(self):
        return get_rooms()

    def submit_schedule(self):
        room = self.room_var.get()
        date = self.date_entry.get()
        subject = self.subject_var.get()
        start_hour = self.start_hour_var.get()
        start_minute = self.start_minute_var.get()
        start_period = self.start_time_period.get()
        end_hour = self.end_hour_var.get()
        end_minute = self.end_minute_var.get()
        end_period = self.end_time_period.get()
        class_name = self.class_name_var.get()
        teacher_id = self.teacher_id  # Use the teacher_id passed during initialization

        # Validate required fields
        if not all([room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name]):
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            insert_schedule(room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, teacher_id)
            messagebox.showinfo("Success", "Schedule inserted successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def go_back(self):
        self.root.destroy()
        os.system(f'python read.py {self.teacher_id}')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create.py <teacher_id>")
        sys.exit(1)

    teacher_id = sys.argv[1]
    root = tk.Tk()
    app = SchedulerApp(root, teacher_id)
    root.mainloop()