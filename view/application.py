from tkinter import Tk, StringVar
from tkinter.ttk import Progressbar, Button, OptionMenu, Label

# All collback functions
def scanNodes():
    pass


# All collback functions
def connectNode():
    pass


root = Tk()
root.title("Crazyflie control client")
root.geometry("840x700")

# Scan button
scanBtn = Button(root, text="Scan", command=scanNodes()).grid(row=0, column=0)

# Dropdown for selecting a quad copter
defaultNode = StringVar(root)
defaultNode.set("Select node")
nodeChoices = {"Select node"}

nodeDropdown = OptionMenu(root, defaultNode, *nodeChoices).grid(row=0, column=1)

# Connect button
connectBtn = Button(root, text="Connect", command=connectNode()).grid(row=0, column=2)

batteryLabel = Label(root, text="Battery:").grid(row=0, column=9)

# Battery indicator
progressBar = Progressbar(root, orient="horizontal", length=120, mode="determinate")
progressBar["value"] = 30
progressBar["maximum"] = 100
progressBar.grid(row=0, column=10)

# Set default size
col_count, row_count = root.grid_size()

for col in range(col_count):
    root.grid_columnconfigure(col, minsize=50, pad=10)

for row in range(row_count):
    root.grid_rowconfigure(row, minsize=50, pad=10)


# Start up and run the GUI
def run():
    root.mainloop()


run()
