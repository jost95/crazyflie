from tkinter import Tk, StringVar
from tkinter.ttk import Progressbar, Button, OptionMenu, Label, Notebook, Frame, Entry


# All collback functions
def scanNodes():
    pass


# All collback functions
def connectNode():
    pass


root = Tk()
root.title("Crazyflie control client")
root.geometry("820x700")
root.resizable(False, False)
root.configure(background='#ECECEC')

# Scan button
scan_btn = Button(root, text="Scan", style="RB.TButton", command=scanNodes()).grid(row=0, column=0)

# Dropdown for selecting a quad copter
default_node = StringVar(root)
default_node.set("Select node")
node_options = {"Select node"}

node_dropdown = OptionMenu(root, default_node, *node_options)
node_dropdown.grid(row=0, column=1)

# Connect button
connect_btn = Button(root, text="Connect", command=connectNode())
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

basic_flight_control_label = Label(flight_control_page, text="Basic flight control")
basic_flight_control_label.grid(row=0, column=0)

flight_mode_label = Label(flight_control_page, text="Flight mode:")
flight_mode_label.grid(row=1, column=0)

# Dropdown for selecting a flight mode
default_flight_mode = StringVar(root)
default_flight_mode.set("Optimal")
flight_mode_options = {"Optimal", "Manual"}

flight_mode_dropdown = OptionMenu(flight_control_page, default_flight_mode, *flight_mode_options)
flight_mode_dropdown.grid(row=1, column=1)

feed_forward_label = Label(flight_control_page, text="Feed forward:")
feed_forward_label.grid(row=2, column=0)

# Dropdown for selecting feedforward mode
default_feedforward_mode = StringVar(root)
default_feedforward_mode.set("Yes")
feed_forward_options = {"Yes", "No"}

flight_mode_dropdown = OptionMenu(flight_control_page, default_feedforward_mode, *feed_forward_options)
flight_mode_dropdown.grid(row=2, column=1)

max_pitch_label = Label(flight_control_page, text="Max pitch/rate:")
max_pitch_label.grid(row=3, column=0)

max_pitch_entry = Entry(flight_control_page, width=10)
max_pitch_entry.grid(row=3, column=1)

max_roll_label = Label(flight_control_page, text="Max roll/rate:")
max_roll_label.grid(row=4, column=0)

max_roll_entry = Entry(flight_control_page)
max_roll_entry.grid(row=4, column=1)

max_thrust_label = Label(flight_control_page, text="Max thrust(%):")
max_thrust_label.grid(row=5, column=0)

max_thrust_entry = Entry(flight_control_page)
max_thrust_entry.grid(row=5, column=1)

manual_control_page = Frame(nb)
nb.add(manual_control_page, text='Manual control')

# Set default size for flight control page
col_count, row_count = flight_control_page.grid_size()

for col in range(col_count):
    flight_control_page.grid_columnconfigure(col, minsize=50, pad=10)

for row in range(row_count):
    flight_control_page.grid_rowconfigure(row, pad=10)

# Set default size for grid
col_count, row_count = root.grid_size()

for col in range(col_count):
    root.grid_columnconfigure(col, minsize=50, pad=10)

for row in range(row_count):
    root.grid_rowconfigure(row, minsize=50, pad=10)


# Start up and run the GUI
def run():
    root.mainloop()


run()
