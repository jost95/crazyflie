import json
import tkinter as tk

from controller import Controller
from application import Application
from signals import Signals
from cflib import crazyflie, crtp

if __name__ == "__main__":
    # Initialize shared signals class
    signals = Signals()

    # Initialize crazyflie
    crtp.init_drivers(enable_debug_driver=True)
    cf = crazyflie.Crazyflie(rw_cache='./cache')

    # Read default config and initialize controller
    with open('config.json') as config_file:
        config = json.load(config_file)
        controller = Controller(cf, config, signals)
        controller.start()

    # Application root
    root = tk.Tk()
    root.title("Crazyflie control client")
    root.geometry("1000x540")
    root.configure(background="#ececec")
    Application(root, cf, signals)

    # Start GUI
    root.mainloop()
