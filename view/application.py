from tkinter import Tk, StringVar, Canvas, Scale, DoubleVar
from tkinter.ttk import Progressbar, Button, OptionMenu, Label, Notebook, Frame, Entry
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
from cflib import crazyflie, crtp
from cflib.crazyflie.log import LogConfig
style.use('ggplot')
matplotlib.use("TkAgg")


# All collback functions
def scanNodes():
    print('Scanning for Crazyflies...')
    available = crtp.scan_interfaces()
    if available:
        print('Found Crazyflies:')
        for i in available:
            print('-', i[0])
        URI = available[0][0]
    else:
        print('No Crazyflies found!')


# All collback functions
def connectNode():
    cf = crazyflie.Crazyflie(rw_cache='./cache')
    print('Connecting to', default_node.get())
    cf.open_link(default_node.get())


root = Tk()
root.title("Crazyflie control client")
root.geometry("1500x900")
root.resizable(False, False)
root.configure(background='#ECECEC')


# Scan button
scan_btn = Button(root, text="Scan", style="RB.TButton", command=lambda: scanNodes())
scan_btn.grid(row=0, column=0)

# Dropdown for selecting a quad copter
default_node = StringVar(root)
default_node.set("Select node")
node_options = {"", "URI1", "URI2"}  # Available 1, 2

node_dropdown = OptionMenu(root, default_node, *node_options)
node_dropdown.grid(row=0, column=1)

# Connect button
connect_btn = Button(root, text="Connect", command=lambda: connectNode())
connect_btn.grid(row=0, column=2)

battery_label = Label(root, text="Battery:")
battery_label.grid(row=0, column=9)

# Battery indicator
progress_bar = Progressbar(root, orient="horizontal", length=120, mode="determinate")
progress_bar["value"] = 30
progress_bar["maximum"] = 100
progress_bar.grid(row=0, column=10)

# Tabs
nb = Notebook(root)
nb.grid(row=1, column=0, columnspan=11, rowspan=13, sticky='NESW')

# Flight control tab
flight_control_page = Frame(nb)
nb.add(flight_control_page, text='Flight control')


# Reference generators
reference_generator_label = Label(flight_control_page, text="Reference generators", font=("helvetica", 13, "bold"))
reference_generator_label.grid(row=0, column=0, sticky="NW")

# Z-Mode
z_mode_label = Label(flight_control_page, text="Z mode:", font=("helvetica", 12))
z_mode_label.grid(row=1, column=0, sticky="NW")

default_z_mode = StringVar(root)
default_z_mode.set("Manual")
z_mode_options = {"", "Manual", "Square wave"}

z_mode = OptionMenu(flight_control_page, default_z_mode, *z_mode_options, )
z_mode.grid(row=1, column=1, sticky="NW")

# X-Mode
x_mode_label = Label(flight_control_page, text="X mode:", font=("helvetica", 12))
x_mode_label.grid(row=2, column=0, sticky="NW")

default_x_mode = StringVar(root)
default_x_mode.set("Manual")
x_mode_options = {"", "Manual", "Square wave"}

x_mode = OptionMenu(flight_control_page, default_x_mode, *x_mode_options)
x_mode.grid(row=2, column=1, sticky="NW")

# Y-Mode
y_mode_label = Label(flight_control_page, text="Y mode:", font=("helvetica", 12))
y_mode_label.grid(row=3, column=0, sticky="NW")

default_y_mode = StringVar(root)
default_y_mode.set("Manual")
y_mode_options = {"", "Manual", "Square wave"}

y_mode = OptionMenu(flight_control_page, default_y_mode, *y_mode_options)
y_mode.grid(row=3, column=1, sticky="NW")


# Manual position parameters
pos_par_label = Label(flight_control_page, text="Manual position parameters", font=("helvetica", 13, "bold"))
pos_par_label.grid(row=4, column=0, sticky="NW")

# Z value
z_pos_label = Label(flight_control_page, text="Z (m):", font=("helvetica", 12))
z_pos_label.grid(row=5, column=0, sticky="NW")

z_pos_entry = Entry(flight_control_page)
z_pos_entry.grid(row=5, column=1, sticky="NW")

# X value
x_pos_label = Label(flight_control_page, text="X (m):", font=("helvetica", 12))
x_pos_label.grid(row=6, column=0, sticky="NW")

x_pos_entry = Entry(flight_control_page)
x_pos_entry.grid(row=6, column=1, sticky="NW")

# Y value
y_pos_label = Label(flight_control_page, text="Y (m):", font=("helvetica", 12))
y_pos_label.grid(row=7, column=0, sticky="NW")

y_pos_entry = Entry(flight_control_page)
y_pos_entry.grid(row=7, column=1, sticky="NW")


# Square wave parameters
square_wave_label = Label(flight_control_page, text="Square wave parameters", font=("helvetica", 13, "bold"))
square_wave_label.grid(row=8, column=0, sticky="NW")

# Amplitude - X
amplitude_x_label = Label(flight_control_page, text="X - Amplitude", font=("helvetica", 12))
amplitude_x_label.grid(row=9, column=0, sticky="NW")

amplitude_x = DoubleVar(root)
amplitude_scale = Scale(flight_control_page, variable=amplitude_x, orient="horizontal", length=180, from_=0, to=10, resolution=0.1)
amplitude_scale.grid(row=9, column=1, sticky="NW")

# Amplitude - Z
amplitude_z_label = Label(flight_control_page, text="Z - Amplitude", font=("helvetica", 12))
amplitude_z_label.grid(row=10, column=0, sticky="NW")

amplitude_z = DoubleVar(root)
amplitude_scale = Scale(flight_control_page, variable=amplitude_z, orient="horizontal", length=180, from_=0, to=10, resolution=0.1)
amplitude_scale.grid(row=10, column=1, sticky="NW")

# Amplitude - Y
amplitude_y_label = Label(flight_control_page, text="Y - Amplitude", font=("helvetica", 12))
amplitude_y_label.grid(row=11, column=0, sticky="NW")

amplitude_y = DoubleVar(root)
amplitude_scale = Scale(flight_control_page, variable=amplitude_y, orient="horizontal", length=180, from_=0, to=10, resolution=0.1)
amplitude_scale.grid(row=11, column=1, sticky="NW")

# Period
period_label = Label(flight_control_page, text="Period", font=("helvetica", 12))
period_label.grid(row=12, column=0, sticky="NW")

period = DoubleVar(root)
period_scale = Scale(flight_control_page, variable=period, orient="horizontal", length=180, from_=0, to=5.0, resolution=0.01)
period_scale.grid(row=12, column=1, sticky="NW")


# Plots for flight data
flight_data_frame = Frame(flight_control_page)
flight_data_frame.grid(row=0, column=4, sticky="NW")

flight_data_label = Label(flight_control_page, text="Flight data", font=("helvetica", 13, "bold"))
flight_data_label.grid(row=0, column=4, sticky="W")

fig = Figure(figsize=(10, 5), facecolor='#ececec')
fig.text(0.5, 0.01, 'Time [ms]', ha='center')
fig.text(0.01, 0.5, 'Output', va='center', rotation='vertical')
ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

graph = FigureCanvasTkAgg(fig, master=flight_control_page)
graph.get_tk_widget().grid(row=1, column=4, sticky="WE", rowspan=10)


# Path Drawer
path_drawer_label = Label(flight_control_page, text="Path drawer", font=("helvetica", 13, "bold"))
path_drawer_label.grid(row=11, column=4, sticky="W")
drawable_canvas = Canvas(flight_control_page, width=700, height=200, bg='#ECECEC')
drawable_canvas.grid(row=12, column=4, sticky="WEN", rowspan=10)


def animate(i):
    pull_data = open('sampleText.txt', 'r').read()
    data_array = pull_data.split('\n')
    xar = []
    yar = []
    for eachLine in data_array:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xar.append(int(x))
            yar.append(int(y))
    ax1.clear()
    ax1.plot(xar, yar)



# Set default size for flight control page
col_count, row_count = flight_control_page.grid_size()

for col in range(col_count):
    flight_control_page.grid_columnconfigure(col, minsize=20, pad=10)

for row in range(row_count):
    flight_control_page.grid_rowconfigure(row, minsize=15, pad=10)


# Set default size for grid
col_count, row_count = root.grid_size()

for col in range(col_count):
    root.grid_columnconfigure(col, minsize=20, pad=10)

for row in range(row_count):
    root.grid_rowconfigure(row, minsize=20, pad=10)


def click(click_event):
    global prev
    prev = click_event


def move(move_event):
    global prev
    drawable_canvas.create_line(prev.x, prev.y, move_event.x, move_event.y, width=2)
    prev = move_event


def remove(click_event):
    global prev
    prev = click_event
    drawable_canvas.delete("all")


drawable_canvas.bind('<Button-1>', click)
drawable_canvas.bind('<B1-Motion>', move)
drawable_canvas.bind('<Button-2>', remove)


# Start up and run the GUI
def run():
    root.mainloop()


#ani = animation.FuncAnimation(fig, animate, interval=1000)

run()
