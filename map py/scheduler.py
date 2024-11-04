import tkinter as tk
import subprocess
import sys

def open_create_file(teacher_id):
    subprocess.Popen(['python', 'create.py', teacher_id])

def open_read_file(teacher_id):
    subprocess.Popen(['python', 'read.py', teacher_id])

def open_status_file(teacher_id):
    subprocess.Popen(['python', 'status.py', teacher_id])

if len(sys.argv) != 2:
    print("Usage: python scheduler.py <teacher_id>")
    sys.exit(1)

teacher_id = sys.argv[1]

# Create the main window
root = tk.Tk()
root.title("Scheduler")

# Set the window size (scale by 3)
default_width = 200
default_height = 150
scaled_width = default_width * 3
scaled_height = default_height * 3

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the position to center the window
x = (screen_width // 2) - (scaled_width // 2)
y = (screen_height // 2) - (scaled_height // 2)

# Set the window geometry
root.geometry(f"{scaled_width}x{scaled_height}+{x}+{y}")

# Define the font for the buttons
button_font = ("Helvetica", 16, "bold")

# Calculate button dimensions
button_width = scaled_width
button_height = scaled_height // 2

# Create buttons
crud_button = tk.Button(root, text="Create, Read, Update, Delete", command=lambda: open_read_file(teacher_id), font=button_font)
status_button = tk.Button(root, text="Status", command=lambda: open_status_file(teacher_id), font=button_font)

# Place buttons
crud_button.place(x=0, y=0, width=button_width, height=button_height)
status_button.place(x=0, y=button_height, width=button_width, height=button_height)

# Run the application
root.mainloop()