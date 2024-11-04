import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
from tkcalendar import DateEntry
import os
import sys
from database import get_schedule, delete_schedule, update_schedule, insert_schedule, get_teacher_ids, get_teacher_name, get_rooms
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
        self.initial_schedule = None  # Variable to store the initial state of the schedule
        self.checkpoint_schedule = None  # Variable to store the checkpoint state of the schedule
        self.modified_schedule = None  # Variable to store the modified state of the schedule

        # Initialize and load schedules
        all_schedules()  # Call the function to initialize and populate the database
        self.load_teacher_schedule(self.teacher_id, save_initial=True)

        # Create buttons
        self.create_buttons()

    def create_tree(self):
        tree = ttk.Treeview(self.root, columns=("Room", "Date", "Subject", "Start Time", "End Time", "Class Name", "Teacher"))
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

        reset_button = tk.Button(button_frame, text="Reset", command=self.reset_schedule)
        reset_button.pack(side=tk.LEFT, padx=5)

        back_button = tk.Button(button_frame, text="Back", command=self.go_back)
        back_button.pack(side=tk.LEFT, padx=5)

        create_button = tk.Button(button_frame, text="Create", command=self.open_create)
        create_button.pack(side=tk.LEFT, padx=5)

        # Create a dropdown menu for switching teachers
        teacher_ids = get_teacher_ids()
        teacher_names = [get_teacher_name(tid) for tid in teacher_ids]
        self.selected_teacher = tk.StringVar(value=get_teacher_name(self.teacher_id))
        switch_menu = tk.OptionMenu(button_frame, self.selected_teacher, *teacher_names, command=self.switch_teacher)
        switch_menu.pack(side=tk.LEFT, padx=5)

    def open_create(self):
        self.root.destroy()
        os.system(f'python create.py {self.teacher_id}')

    def load_schedule(self, schedule):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not schedule:
            messagebox.showinfo("Info", "The schedule is empty.")
        else:
            for entry in schedule:
                self.tree.insert("", "end", text=entry["id"], values=(entry["room"], entry["date"], entry["subject"], f"{entry['start_hour']}:{entry['start_minute']} {entry['start_period']}", f"{entry['end_hour']}:{entry['end_minute']} {entry['end_period']}", entry["class_name"], entry["teacher_name"]))

    def load_teacher_schedule(self, teacher_id, save_initial=False):
        schedule = get_schedule()
        teacher_schedule = [entry for entry in schedule if entry["teacher_id"] == teacher_id]
        if save_initial:
            self.initial_schedule = teacher_schedule.copy()  # Save the initial state of the schedule
            self.checkpoint_schedule = teacher_schedule.copy()  # Save the initial state as the first checkpoint
        self.modified_schedule = teacher_schedule.copy()  # Save the modified state of the schedule
        self.load_schedule(teacher_schedule)

    def on_double_click(self, event):
        item_id = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)
        column_index = int(column[1:]) - 1
        item = self.tree.item(item_id)
        values = item['values']
        if values[6] != get_teacher_name(self.teacher_id):
            messagebox.showerror("Error", "You can only edit your own schedule.")
            return
        if column_index == 0:  # Room column
            new_value = self.get_room_dropdown(values[column_index])
        else:
            new_value = self.get_new_value(column_index, values[column_index])
        if new_value is not None:
            self.undo_stack.append(("edit", values))
            self.redo_stack.clear()  # Clear the redo stack on new action
            values[column_index] = new_value
            room, date, subject, start_time, end_time, class_name, teacher_name = values
            start_hour, start_minute, start_period = start_time.split(':')[0], start_time.split(':')[1].split(' ')[0], start_time.split(' ')[1]
            end_hour, end_minute, end_period = end_time.split(':')[0], end_time.split(':')[1].split(' ')[0], end_time.split(' ')[1]
            updated_values = (room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, self.teacher_id)
            self.update_modified_schedule(item_id, updated_values)
            self.load_teacher_schedule(self.teacher_id)

    def get_new_value(self, column_index, current_value):
        if self.tree['columns'][column_index] == "Date":
            return self.get_date(current_value)
        else:
            return simpledialog.askstring("Input", f"Enter new value for {self.tree['columns'][column_index]}:", initialvalue=current_value)

    def get_date(self, initial_value):
        date_dialog = tk.Toplevel(self.root)
        date_dialog.title("Select Date")
        try:
            parsed_date = datetime.strptime(initial_value, '%Y-%m-%d')
        except ValueError:
            parsed_date = datetime.strptime(initial_value, '%m/%d/%y')
        date_entry = DateEntry(date_dialog, selectmode='day', mindate=date.today(), year=parsed_date.year, month=parsed_date.month, day=parsed_date.day)
        date_entry.pack(pady=20)

        def save_date():
            date_dialog.destroy()

        save_button = tk.Button(date_dialog, text="Save", command=save_date)
        save_button.pack(pady=10)

        date_dialog.wait_window()
        return date_entry.get_date().strftime('%Y-%m-%d')

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

    def update_modified_schedule(self, item_id, updated_values):
        print(f"Updating item with ID {item_id} with values {updated_values}")
        found = False
        for entry in self.modified_schedule:
            if entry["id"] == item_id:
                entry.update({
                    "room": updated_values[0],
                    "date": updated_values[1],
                    "subject": updated_values[2],
                    "start_hour": updated_values[3],
                    "start_minute": updated_values[4],
                    "start_period": updated_values[5],
                    "end_hour": updated_values[6],
                    "end_minute": updated_values[7],
                    "end_period": updated_values[8],
                    "class_name": updated_values[9],
                    "teacher_id": updated_values[10]
                })
                print(f"Updated entry: {entry}")
                found = True
                break
        if not found:
            print(f"No entry found with ID {item_id}")

    def save_schedule(self):
        print("Saving schedule...")
        for entry in self.modified_schedule:
            room = entry["room"]
            date = entry["date"]
            subject = entry["subject"]
            start_hour = entry["start_hour"]
            start_minute = entry["start_minute"]
            start_period = entry["start_period"]
            end_hour = entry["end_hour"]
            end_minute = entry["end_minute"]
            end_period = entry["end_period"]
            class_name = entry["class_name"]
            teacher_id = entry["teacher_id"]
            updated_values = (room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, teacher_id)
            print(f"Updating schedule with values: {updated_values}")
            insert_schedule(room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, teacher_id)
        self.checkpoint_schedule = self.modified_schedule.copy()  # Save the current state as the checkpoint
        print("Schedule saved.")

    def remove_row(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            values = item['values']
            if values[6] != get_teacher_name(self.teacher_id):
                messagebox.showerror("Error", "You can only remove your own schedule.")
                return
            self.undo_stack.append(("remove", values))
            self.redo_stack.clear()  # Clear the redo stack on new action
            self.tree.delete(selected_item)
            room, date, subject, start_time, end_time, class_name, teacher_name = values
            start_hour, start_minute, start_period = start_time.split(':')[0], start_time.split(':')[1].split(' ')[0], start_time.split(' ')[1]
            delete_schedule(room, date, start_hour, start_minute, start_period)

    def undo_action(self):
        if self.undo_stack:
            action, values = self.undo_stack.pop()
            self.redo_stack.append((action, values))
            if action == "edit":
                room, date, subject, start_time, end_time, class_name, teacher_name = values
                start_hour, start_minute, start_period = start_time.split(':')[0], start_time.split(':')[1].split(' ')[0], start_time.split(' ')[1]
                end_hour, end_minute, end_period = end_time.split(':')[0], end_time.split(':')[1].split(' ')[0], end_time.split(' ')[1]
                updated_values = (room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, self.teacher_id)
                self.update_modified_schedule(values[0], updated_values)
            elif action == "remove":
                room, date, subject, start_time, end_time, class_name, teacher_name = values
                start_hour, start_minute, start_period = start_time.split(':')[0], start_time.split(':')[1].split(' ')[0], start_time.split(' ')[1]
                end_hour, end_minute, end_period = end_time.split(':')[0], end_time.split(':')[1].split(' ')[0], end_time.split(' ')[1]
                insert_schedule(room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, self.teacher_id)
            self.load_teacher_schedule(self.teacher_id)

    def redo_action(self):
        if self.redo_stack:
            action, values = self.redo_stack.pop()
            self.undo_stack.append((action, values))
            if action == "edit":
                room, date, subject, start_time, end_time, class_name, teacher_name = values
                start_hour, start_minute, start_period = start_time.split(':')[0], start_time.split(':')[1].split(' ')[0], start_time.split(' ')[1]
                end_hour, end_minute, end_period = end_time.split(':')[0], end_time.split(':')[1].split(' ')[0], end_time.split(' ')[1]
                updated_values = (room, date, subject, start_hour, start_minute, start_period, end_hour, end_minute, end_period, class_name, self.teacher_id)
                self.update_modified_schedule(values[0], updated_values)
            elif action == "remove":
                room, date, subject, start_time, end_time, class_name, teacher_name = values
                start_hour, start_minute, start_period = start_time.split(':')[0], start_time.split(':')[1].split(' ')[0], start_time.split(' ')[1]
                end_hour, end_minute, end_period = end_time.split(':')[0], end_time.split(':')[1].split(' ')[0], end_time.split(' ')[1]
                delete_schedule(room, date, start_hour, start_minute, start_period)
            self.load_teacher_schedule(self.teacher_id)

    def reset_schedule(self):
        if self.checkpoint_schedule is not None:
            self.modified_schedule = self.checkpoint_schedule.copy()  # Update modified_schedule to match checkpoint
            self.load_schedule(self.checkpoint_schedule)
            self.checkpoint_schedule = self.modified_schedule.copy()  # Save the reset state as the new checkpoint

    def go_back(self):
        if self.modified_schedule == self.checkpoint_schedule:
            os.system(f'python scheduler.py {self.teacher_id}')
        else:
            response = messagebox.askyesno("Confirm", "Do you want to discard changes and go back?")
            if response:  # Discard changes
                self.reset_schedule()  # Revert to last saved checkpoint
                os.system(f'python scheduler.py {self.teacher_id}')
            # If response is False, do nothing (stay in the current window)

    def switch_teacher(self, selected_teacher_name):
        teacher_ids = get_teacher_ids()
        teacher_names = [get_teacher_name(tid) for tid in teacher_ids]
        teacher_id = teacher_ids[teacher_names.index(selected_teacher_name)]
        self.teacher_id = teacher_id  # Update the current teacher_id
        self.load_teacher_schedule(teacher_id)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read.py <teacher_id>")
        sys.exit(1)

    teacher_id = sys.argv[1]
    root = tk.Tk()
    app = ScheduleViewerApp(root, teacher_id)
    root.mainloop()