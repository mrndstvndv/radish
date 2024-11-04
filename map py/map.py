import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Slider
import tkinter as tk

rooms = {
    "CL-A": (200, 180, 370, 280),
    "CL-B": (370, 180, 540, 280),
    "CL-C": (540, 180, 710, 280),
    "CL-E": (255, 300, 425, 400),
    "CL-F": (425, 300, 655, 350),
    "CL-G": (425, 350, 655, 400),
    "SUB OFFICE": (230, 430, 370, 530),
    "TECH OFFICE": (310, 430, 370, 490),
    "L3": (370, 430, 450, 530),
    "L4": (450, 430, 530, 530),
    "CL-D": (530, 430, 710, 530),
    "CR-M": (60, 120, 100, 180),
    "CR-F": (100, 120, 140, 180),
    "L1": (60, 180, 140, 260),
    "L2": (60, 260, 140, 340),
}

def draw_2d_map():
    fig, ax = plt.subplots()
    for room, (x1, y1, x2, y2) in rooms.items():
        width = x2 - x1
        height = y2 - y1
        rect = patches.Rectangle((x1, y1), width, height, edgecolor='black', facecolor='lightgrey')
        ax.add_patch(rect)
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    ax.axis('off')  # Hide the axes
    return fig

def draw_3d_map():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for room_name, (x1, y1, x2, y2) in rooms.items():
        z = 0  # Base height for all rooms
        height = 50 / 3  # New height
        verts = [
            [(x1, y1, z), (x2, y1, z), (x2, y2, z), (x1, y2, z)],  # Bottom face
            [(x1, y1, z+height), (x2, y1, z+height), (x2, y2, z+height), (x1, y2, z+height)],  # Top face
            [(x1, y1, z), (x1, y1, z+height), (x1, y2, z+height), (x1, y2, z)],  # Side faces
            [(x2, y1, z), (x2, y1, z+height), (x2, y2, z+height), (x2, y2, z)],
            [(x1, y1, z), (x2, y1, z), (x2, y1, z+height), (x1, y1, z+height)],
            [(x1, y2, z), (x2, y2, z), (x2, y2, z+height), (x1, y2, z+height)],
        ]
        ax.add_collection3d(Poly3DCollection(verts, facecolors='lightgrey', edgecolors='black'))
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 600)
    ax.set_zlim(0, 100)
    ax.set_axis_off()

    # Define the update function for the slider
    def update(val):
        angle = slider.val
        ax.view_init(azim=angle)
        plt.draw()

    # Add a slider to control the rotation
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Angle', 0, 360, valinit=0)
    slider.on_changed(update)
    
    # Add a button to switch back to 2D map
    def switch_to_2d():
        plt.close(fig)
        root.deiconify()

    button_ax = plt.axes([0.45, 0.005, 0.1, 0.04])
    button = plt.Button(button_ax, '2D Map', color='lightgoldenrodyellow', hovercolor='0.975')
    button.on_clicked(lambda event: switch_to_2d())

    plt.show()

def switch_to_3d():
    root.withdraw()
    draw_3d_map()
    root.deiconify()

root = tk.Tk()
root.title("2D and 3D Map Viewer")

fig = draw_2d_map()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

button = tk.Button(root, text="Switch to 3D Map", command=switch_to_3d)
button.pack(pady=20)

root.mainloop()