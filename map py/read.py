import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from tkcalendar import DateEntry, dateentry
import os
import sys
from database import (
    get_schedule,
    delete_schedule,
    update_schedule,
    insert_schedule,
    get_teacher_ids,
    get_teacher_name,
    get_rooms,
)
from data import all_schedules
from datetime import date, datetime


class ScheduleViewerApp:
    def __init__(self, root, teacher_id):
        self.root = root
        self.teacher_id = teacher_id
        self.root.title("Schedule Viewer")
        self.tree = self.create_tree()
        self.undo_stack = []
        self.redo_stack = []
        self.initial_schedule = (
            None  # Variable to store the initial state of the schedule
        )
        self.checkpoint_schedule = (
            None  # Variable to store the checkpoint state of the schedule
        )
        self.modified_schedule = (
            None  # Variable to store the modified state of the schedule
        )

        # Initialize and load schedules
        all_schedules()  # Call the function to initialize and populate the database
        self.load_teacher_schedule(self.teacher_id)

        # Create buttons
        self.create_buttons()

    def create_tree(self):
        tree = ttk.Treeview(
            self.root,
            columns=(
                "Room",
                "Date",
                "Subject",
                "Start Time",
                "End Time",
                "Class Name",
                "Teacher",
            ),
        )
        tree.heading("#0", text="ID")
        tree.heading("#1", text="Room")
        tree.heading("#2", text="Date")
        tree.heading("#3", text="Subject")
        tree.heading("#4", text="Start Time")
        tree.heading("#5", text="End Time")
        tree.heading("#6", text="Class Name")
        tree.heading("#7", text="Teacher")

        # Hide the ID column
        tree.column("#0", width=0, stretch=tk.NO)

        tree.pack(fill=tk.BOTH, expand=True)
        tree.bind("<Double-1>", self.on_double_click)
        return tree

    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        save_button = tk.Button(button_frame, text="Save", command=self.save_schedule)
        save_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Delete", command=self.remove_row)
        delete_button.pack(side=tk.LEFT, padx=5)

        undo_button = tk.Button(button_frame, text="Undo", command=self.undo_action)
        undo_button.pack(side=tk.LEFT, padx=5)

        redo_button = tk.Button(button_frame, text="Redo", command=self.redo_action)
        redo_button.pack(side=tk.LEFT, padx=5)

        reset_button = tk.Button(
            button_frame, text="Reset", command=self.reset_schedule
        )
        reset_button.pack(side=tk.LEFT, padx=5)

        back_button = tk.Button(button_frame, text="Back", command=self.go_back)
        back_button.pack(side=tk.LEFT, padx=5)

        create_button = tk.Button(button_frame, text="Create", command=self.open_create)
        create_button.pack(side=tk.LEFT, padx=5)

        # Create a dropdown menu for switching teachers
        teacher_ids = get_teacher_ids()
        teacher_names = [get_teacher_name(tid) for tid in teacher_ids]
        self.selected_teacher = tk.StringVar(value=get_teacher_name(self.teacher_id))
        switch_menu = tk.OptionMenu(
            button_frame,
            self.selected_teacher,
            *teacher_names,
            command=self.switch_teacher,
        )
        switch_menu.pack(side=tk.LEFT, padx=5)

    def open_create(self):
        self.root.destroy()
        os.system(f"python create.py {self.teacher_id}")

    def load_teacher_schedule(self, teacher_id):
        sched = get_schedule()

        # save for reset
        self.initial_schedule = sched.copy()
        self.modified_schedule = sched.copy()
        print("sched: ", sched)

        self.load_schedule(sched)

    def load_schedule(self, schedule):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not schedule:
            messagebox.showinfo("Info", "The schedule is empty.")
        else:
            for entry in schedule:
                self.tree.insert(
                    "",
                    "end",
                    text=entry["id"],
                    values=(
                        entry["room"],
                        entry["date"],
                        entry["subject"],
                        f"{entry['start_hour']}:{entry['start_minute']} {entry['start_period']}",
                        f"{entry['end_hour']}:{entry['end_minute']} {entry['end_period']}",
                        entry["class_name"],
                        entry["teacher_name"],
                    ),
                )

    def update_modified_schedule(self, item_id, updated_values):
        raise NotImplementedError()

    def save_schedule(self):
        # TODO: update the db itself
        for item in self.modified_schedule:
            # TODO: we can check the stack for modifications so we do not waste resources
            update_schedule(
                item,
            )

    def remove_row(self):
        raise NotImplementedError()

    def undo_action(self):
        raise NotImplementedError()

    def redo_action(self):
        raise NotImplementedError()

    def reset_schedule(self):
        raise NotImplementedError()

    def go_back(self):
        raise NotImplementedError()

    def switch_teacher(self, selected_teacher_name):
        raise NotImplementedError()

    def get_key(self, key: str) -> str:
        key = key.lower()

        print(key)

        # TODO: add other cases
        if key == "teacher":
            return "teacher_id"

        return key

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        item_index = self.tree.index(item_id)
        item = self.modified_schedule[item_index].copy()

        column = self.tree.identify_column(event.x)
        column_index = int(column.replace("#", "")) - 1
        column_name = self.tree.heading(column)["text"]

        print("row:", item_index, "column", column_index)
        key = self.get_key(column_name)

        # TODO: add guard where the teacher can only edit his own schedule

        match column_name:
            case "Room":
                new_value = self.get_room_dropdown(item[key])
            case "Date":
                new_value = self.get_date(item[key])


        item[key] = new_value

        # WARN: Update shit
        self.modified_schedule[item_index] = item
        self.undo_stack.append(("edit", item_index, key, new_value))
        self.load_schedule(self.modified_schedule)
        print("Item added to undo stack: ", self.undo_stack)

    def get_new_value(self, column_index, current_value):
        if self.tree["columns"][column_index] == "Date":
            return self.get_date(current_value)
        else:
            return simpledialog.askstring(
                "Input",
                f"Enter new value for {self.tree['columns'][column_index]}:",
                initialvalue=current_value,
            )

    def get_date(self, initial_value):
        date_dialog = tk.Toplevel(self.root)
        date_dialog.title("Select Date")
        try:
            parsed_date = datetime.strptime(initial_value, "%Y-%m-%d")
        except ValueError:
            parsed_date = datetime.strptime(initial_value, "%m/%d/%y")
        date_entry = DateEntry(
            date_dialog,
            selectmode="day",
            mindate=date.today(),
            year=parsed_date.year,
            month=parsed_date.month,
            day=parsed_date.day,
        )
        date_entry.pack(pady=20)

        def save_date():
            global out_date
            out_date = date_entry.get_date().strftime("%m/%d/%y")
            date_dialog.destroy()


        save_button = tk.Button(date_dialog, text="Save", command=save_date)
        save_button.pack(pady=10)

        print("run")
        date_dialog.wait_window()

        return out_date

    def get_room_dropdown(self, current_value):
        room_dialog = tk.Toplevel(self.root)
        room_dialog.title("Select Room")

        room_var = tk.StringVar(value=current_value)
        room_menu = ttk.Combobox(room_dialog, textvariable=room_var, values=get_rooms())
        room_menu.pack(pady=20)

        def save_room():
            room_dialog.destroy()

        save_button = tk.Button(room_dialog, text="Save", command=save_room)
        save_button.pack(pady=10)

        room_dialog.wait_window()
        return room_var.get()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read.py <teacher_id>")
        sys.exit(1)

    teacher_id = sys.argv[1]
    root = tk.Tk()
    app = ScheduleViewerApp(root, teacher_id)
    root.mainloop()
