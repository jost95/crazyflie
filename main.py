import json
import tkinter as tk
import time

from controller import Controller
from application import Application
from signals import Signals


def graceful_shutdown(s_root, s_cf):
    s_cf.close_link()
    s_root.destroy()


if __name__ == "__main__":
    # Initialize shared signals class
    signals = Signals()

    # Read default config and initialize controller
    with open('config.json') as config_file:
        config = json.load(config_file)
        controller = Controller(config, signals)
        controller.start()

    # Wait for controller to be initialized
    while not signals.cf_setup():
        time.sleep(0.1)

    cf = controller.get_cf()

    # Application root
    root = tk.Tk()
    root.title("Crazyflie control client")
    root.geometry("1000x540")
    root.configure(background="#ececec")
    Application(root, cf, signals)

    root.protocol("WM_DELETE_WINDOW", lambda: graceful_shutdown(root, cf))

    # Start GUI
    root.mainloop()
