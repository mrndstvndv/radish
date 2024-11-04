import tkinter as tk
from tkinter import messagebox
from database import insert_teacher_id
import re

def validate_teacher_id(teacher_id):
    pattern = re.compile(r'^\d{2}-\d{5}$')
    return pattern.match(teacher_id) is not None

def add_teacher_id():
    teacher_id = entry_id.get()
    if validate_teacher_id(teacher_id):
        insert_teacher_id(teacher_id)
        messagebox.showinfo("Success", "Teacher ID added successfully!")
        entry_id.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Invalid Teacher ID format. It should be in the format XX-XXXXX where X is a digit.")

# Create the main window
root = tk.Tk()
root.title("Add Teacher ID")

# Set the window size and position it in the center of the screen
window_width = 300
window_height = 150
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

# Create and place the widgets
label_id = tk.Label(root, text="New Teacher ID:")
label_id.pack(pady=10)
entry_id = tk.Entry(root)
entry_id.pack(pady=5)
add_button = tk.Button(root, text="Add", command=add_teacher_id)
add_button.pack(pady=10)

# Run the application
root.mainloop()