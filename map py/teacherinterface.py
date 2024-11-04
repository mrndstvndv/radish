import tkinter as tk
from tkinter import messagebox
from database import get_teacher_ids, insert_teacher, get_teacher_name
import subprocess

def open_scheduler(teacher_id):
    subprocess.Popen(['python', 'scheduler.py', teacher_id])

def open_schedule_viewer(teacher_id):
    subprocess.Popen(['python', 'read.py', teacher_id])

def update_teacher_name(teacher_id):
    def save_name():
        teacher_name = entry_name.get()
        insert_teacher(teacher_id, teacher_name)
        messagebox.showinfo("Update Success", "Name updated successfully!")
        name_window.destroy()
        open_scheduler(teacher_id)  # Open the scheduler after saving the name

    def on_close():
        root.destroy()

    teacher_name = get_teacher_name(teacher_id)
    if teacher_name:
        open_scheduler(teacher_id)
    else:
        name_window = tk.Toplevel(root)
        name_window.title("Enter Teacher Name")
        name_window.geometry("300x150")
        name_window.protocol("WM_DELETE_WINDOW", on_close)

        label_name = tk.Label(name_window, text="Teacher Name:")
        label_name.pack(pady=10)
        entry_name = tk.Entry(name_window)
        entry_name.pack(pady=5)
        save_button = tk.Button(name_window, text="Save", command=save_name)
        save_button.pack(pady=10)

def login():
    teacher_id = entry_id.get()
    if teacher_id in get_teacher_ids():
        messagebox.showinfo("Login Success", "Welcome!")
        update_teacher_name(teacher_id)
    else:
        messagebox.showerror("Login Failed", "Invalid ID")

# Create the main window
root = tk.Tk()
root.title("Teacher Login")

# Set the window size and position it in the center of the screen
window_width = 300
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Create and place the widgets
label_id = tk.Label(root, text="Teacher ID:")
label_id.pack(pady=10)
entry_id = tk.Entry(root)
entry_id.pack(pady=5)
login_button = tk.Button(root, text="Login", command=login)
login_button.pack(pady=10)

root.mainloop()