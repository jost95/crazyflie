import tkinter as tk
import tkinter.ttk as ttk
import time
import matplotlib
import numpy as np

from cflib import crtp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style

from tkinter import messagebox

matplotlib.use("TkAgg")
style.use("ggplot")


class Application:
    HEADER_FONT = "Helvetica 15 bold"
    BOLD_FONT = "Helvetica 13 bold"
    BG_COLOR = "#ececec"

    def scan_nodes(self):
        available = crtp.scan_interfaces()

        menu = self.radio_dropdown["menu"]
        menu.delete(0, "end")

        if available:
            self.connect_btn['state'] = 'normal'

            for r in available:
                radio = r[0]
                menu.add_command(label=radio, command=lambda value=radio: self.selected_radio.set(value))
        else:
            messagebox.showwarning("Warning", "No Crazyflie radios found")

    @staticmethod
    def set_entry(entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def toggle_connection(self):
        if self.signals.read_connection():
            self.cf.close_link()
            
            count = 0
            while self.signals.read_connection() and count < 5:
                time.sleep(1)
                count += 1

            if self.signals.read_connection():
                messagebox.showerror("Error", "Could not disconnect from Crazyflie radio")
            else:
                self.scan_btn['state'] = 'normal'
                self.connect_btn['state'] = 'disabled'
                self.engines_btn['state'] = 'disabled'
                self.connect_btn_text.set("Connect")
                self.engines_btn_text.set("Start engines")

        else:
            self.cf.open_link(self.selected_radio.get())

            count = 0
            while not self.signals.read_connection() and count < 5:
                time.sleep(1)
                count += 1

            if not self.signals.read_connection():
                messagebox.showerror("Error", "Could not connect to Crazyflie radio, trying to shutdown")
                self.cf.close_link()
            else:
                self.scan_btn['state'] = 'disabled'
                self.engines_btn['state'] = 'normal'
                self.connect_btn_text.set("Disconnect")

                # Wait for good position estimate from controller thread
                ref_pos = self.signals.get_ref_position()
                
                count = 0
                while ref_pos[0] == 0 and count < 5:
                    time.sleep(1)
                    ref_pos = self.signals.get_ref_position()
                    count += 1

                if count == 5:
                    messagebox.showerror("Error", "Could not get position estimate, disconnecting...")
                    self.toggle_connection()
                else:
                    # Update the current reference values
                    self.set_entry(self.xref_entry, round(ref_pos[0],2))
                    self.set_entry(self.yref_entry, round(ref_pos[1],2))
                    self.set_entry(self.zref_entry, round(ref_pos[2],2))

    def toggle_engines(self):
        self.signals.switch_toggle()

        if self.engines_on:
            self.engines_btn_text.set("Start engines")
        else:
            self.engines_btn_text.set("Stop engines")

    def update_xref(self, e):
        del e
        self.signals.set_xref_position(self.xref_entry.get())

    def update_yref(self, e):
        del e
        self.signals.set_yref_position(self.yref_entry.get())

    def update_zref(self, e):
        del e
        self.signals.set_zref_position(self.zref_entry.get())

    def __init__(self, root, cf, signals, fig):
        super(Application, self).__init__()

        self.fig = fig
        self.root = root
        self.cf = cf
        self.signals = signals
        self.prev_event = 0
        self.canvas_time_start = 0

        self.engines_on = True

        # ----- TOP MENU -----
        top_menu = ttk.Frame(self.root)

        # Scan button
        self.scan_btn = ttk.Button(top_menu, text="Scan", command=self.scan_nodes)
        self.scan_btn.pack(side=tk.LEFT)

        # Dropdown for selecting a quad copter
        self.selected_radio = tk.StringVar(self.root)
        self.selected_radio.set("Select radio")

        self.radio_dropdown = ttk.OptionMenu(top_menu, self.selected_radio, "Select radio")
        self.radio_dropdown.pack(side=tk.LEFT)

        # Connect button
        self.connect_btn_text = tk.StringVar(self.root)
        self.connect_btn_text.set("Connect")
        self.connect_btn = ttk.Button(top_menu, textvariable=self.connect_btn_text, state=tk.DISABLED,
                                      command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT)

        # Toggle engines button
        self.engines_btn_text = tk.StringVar(self.root)
        self.engines_btn_text.set("Start engines")
        self.engines_btn = ttk.Button(top_menu, textvariable=self.engines_btn_text, state=tk.DISABLED,
                                      command=self.toggle_engines)
        self.engines_btn.pack(side=tk.LEFT)
        # ----- END TOP MENU ------

        # ----- LEFT MENU -----
        left_menu = ttk.Frame(self.root)

        ttk.Label(left_menu, text="Set reference", font=self.HEADER_FONT) \
            .grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Frame(left_menu, height=1, bg="grey") \
            .grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        ttk.Label(left_menu, text="Axis", font=self.BOLD_FONT) \
            .grid(row=2, column=0, sticky="w")

        ttk.Label(left_menu, text="Reference", font=self.BOLD_FONT) \
            .grid(row=2, column=1, sticky="w")

        # ----- X MODE -----
        ttk.Label(left_menu, text="X").grid(row=3, column=0, sticky="w")

        self.xref_entry = ttk.Entry(left_menu, width=4)
        self.xref_entry.grid(row=3, column=1, sticky="w")
        self.xref_entry.bind('<Return>', self.update_xref)
        # ----- END X MODE -----

        # ----- Y MODE -----
        ttk.Label(left_menu, text="Y").grid(row=4, column=0, sticky="w")

        self.yref_entry = ttk.Entry(left_menu, width=4)
        self.yref_entry.grid(row=4, column=1, sticky="w")
        self.yref_entry.bind('<Return>', self.update_yref)

        # ----- Z MODE -----
        ttk.Label(left_menu, text="Z").grid(row=5, column=0, sticky="w")

        self.zref_entry = ttk.Entry(left_menu, width=4)
        self.zref_entry.grid(row=5, column=1, sticky="w")
        self.zref_entry.bind('<Return>', self.update_zref)

        # ----- CANVAS ------
        ttk.Label(left_menu, text="XY path drawer", font=self.HEADER_FONT) \
            .grid(row=6, column=0, columnspan=4, sticky="sw", pady=5)

        tk.Frame(left_menu, height=1, bg="grey") \
            .grid(row=7, column=0, columnspan=4, sticky="ew")

        self.drawable_canvas = tk.Canvas(left_menu, width=300, height=300, bg='#ECECEC')
        self.drawable_canvas.grid(row=8, column=0, columnspan=4, pady=5)
        self.drawable_canvas.bind('<Button-1>', self.click)
        self.drawable_canvas.bind('<B1-Motion>', self.move)
        self.drawable_canvas.bind('<ButtonRelease-1>', self.clear_canvas)

        left_menu.columnconfigure(0, minsize=40)
        left_menu.columnconfigure(1, minsize=130)
        left_menu.columnconfigure(2, minsize=60)

        # ----- FLIGHT PLOTS -----
        flight_plots = ttk.Frame(self.root)

        ttk.Label(flight_plots, text="Flight plots", font=self.HEADER_FONT) \
            .grid(row=0, column=0, sticky="w")

        tk.Frame(flight_plots, height=1, bg="grey") \
            .grid(row=1, column=0, sticky="ew", pady=5)

        self.graph = FigureCanvasTkAgg(self.fig, master=flight_plots)
        self.graph.get_tk_widget().grid(row=2, column=0, sticky="we")

        # ----- GRID PLACEMENT -----
        top_menu.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        left_menu.grid(row=1, column=0, sticky="nw", padx=10)
        flight_plots.grid(row=1, column=1, sticky="nw", padx=10)

    def click(self, click_event):
        self.canvas_time_start = time.time()
        xy = np.r_[click_event.x, click_event.y]
        self.signals.set_canvas_xy(xy, xy)
        self.prev_event = click_event

    def move(self, move_event):
        self.drawable_canvas.create_line(self.prev_event.x, self.prev_event.y, move_event.x, move_event.y, width=2)

        if self.canvas_time_start + 0.02 < time.time():
            xy = np.r_[move_event.x, move_event.y]
            xy_prev = np.r_[self.prev_event.x, self.prev_event.y]
            self.signals.set_canvas_xy(xy, xy_prev)
            self.canvas_time_start = time.time()
        
        self.prev_event = move_event

    def clear_canvas(self, click_event):
        del click_event
        time.sleep(0.3)
        xy = np.r_[0,0]
        self.signals.set_canvas_xy(xy, xy)
        self.drawable_canvas.delete("all")

