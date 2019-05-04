import tkinter as tk
import json
import time
import matplotlib
import numpy as np
import threading
import os

from random import randint
from controller import Controller
from application import Application
from signals import Signals

from matplotlib import pyplot as plt
from matplotlib import animation as animation
from matplotlib import style

# Set styles for plots
matplotlib.use("TkAgg")
style.use("ggplot")

# Define sub plots
fig, axe_matrix = plt.subplots(2, 2)
fig.set_facecolor("#ececec")
lines = []
signals = Signals()

x_axe = axe_matrix[0, 0]
y_axe = axe_matrix[0, 1]
z_axe = axe_matrix[1, 0]
c_axe = axe_matrix[1, 1]

axes = [x_axe, y_axe, z_axe, c_axe]

# Get the graph lines
for axe in axes:
    axe.grid()

    line1, = axe.plot([], [])
    line2, = axe.plot([], [])

    lines.append(line1)
    lines.append(line2)


# Updates the plot
def plotter(frame):
    del frame
    plot_data = signals.get_for_plotter()
    time_data = plot_data[0]

    # axis limits checking. Same as before, just for both axes
    k = 1
    for ax in axes:
        ax.set_xlim(min(time_data), max(time_data) + 0.1)
        if k == 7:
            ax.set_ylim(min(plot_data[k]) - 3, max(plot_data[k]) + 3)
        else:
            ax.set_ylim(min([min(plot_data[k]), min(plot_data[k + 1])]) - 3,
                        max([max(plot_data[k]), max(plot_data[k + 1])]) + 3)

        ax.figure.canvas.draw()
        k += 2

    k = 1
    for l in lines:
        if not k == 8:
            l.set_data(time_data, plot_data[k])

        k += 1

    return lines


def graceful_shutdown(s_root, s_cf):
    s_cf.close_link()
    s_root.destroy()
    os._exit(1)


def rand_data():
    t0 = time.time()
    time.sleep(0.03)

    while True:
        t = time.time() - t0
        signals.set_for_plotter(t, np.r_[randint(1, 5), randint(1, 5), randint(1, 5)], signals.get_ref_position(),
                                randint(1, 5))

        time.sleep(0.03)


# Initialize random signal generator
random_thread = threading.Thread(target=rand_data)
random_thread.daemon = True
random_thread.start()

# Read default config and initialize controller
with open('config.json') as config_file:
    config = json.load(config_file)

# Initialize controller and get crazyflie
controller = Controller(config, signals)
cf = controller.get_cf()
controller.start()

# Application root
root = tk.Tk()
root.title("Crazyflie control client")
root.geometry("1000x540")
root.configure(background="#ececec")
root.resizable(False, False)

# Define a new application
Application(root, cf, signals, fig)

ani = animation.FuncAnimation(fig, plotter, frames=1, interval=1000, blit=True)

root.protocol("WM_DELETE_WINDOW", lambda: graceful_shutdown(root, cf))

# Start GUI
root.mainloop()
