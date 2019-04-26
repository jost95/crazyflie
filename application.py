import tkinter as tk
import tkinter.ttk as ttk
import time
import matplotlib
import numpy as np
import threading
from random import randint

from cflib import crtp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as MCanvas
from matplotlib.figure import Figure as MFigure

from tkinter import messagebox

matplotlib.use("TkAgg")


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
        if self.cf.is_connected():
            self.cf.close_link()

            if self.cf.is_connected():
                messagebox.showerror("Error", "Could not disconnect from Crazyflie radio")
            else:
                self.scan_btn['state'] = 'normal'
                self.connect_btn['state'] = 'disabled'
                self.engines_btn['state'] = 'disabled'
                self.connect_btn_text.set("Connect")
                self.engines_btn_text.set("Start engines")

        else:
            self.cf.open_link(self.selected_radio.get())

            if not self.cf.is_connected():
                messagebox.showerror("Error", "Could not connect to Crazyflie radio")
            else:
                self.scan_btn['state'] = 'disabled'
                self.engines_btn['state'] = 'normal'
                self.connect_btn_text.set("Disconnect")

                # Wait for good position estimate from controller thread
                ref_pos = self.signals.get_ref_position()

                while ref_pos[0] == 0:
                    time.sleep(0.2)
                    ref_pos = self.signals.get_ref_position()

                # Update the current reference values
                self.set_entry(self.xref_entry, ref_pos[0])
                self.set_entry(self.yref_entry, ref_pos[1])
                self.set_entry(self.zref_entry, ref_pos[2])

    def toggle_engines(self):
        self.signals.switch_toggle()

        if self.engines_on:
            self.engines_btn_text.set("Start engines")
        else:
            self.engines_btn_text.set("Stop engines")

    def update_xref(self):
        self.signals.set_xref_position(self.xref_entry.get())

    def update_yref(self):
        self.signals.set_yref_position(self.yref_entry.get())

    def update_zref(self):
        self.signals.set_zref_position(self.zref_entry.get())

    def __init__(self, root, cf, signals):
        super(Application, self).__init__()

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
                                      command=self.toggle_connection)
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

        # ----- END LEFT MENU -----
        flight_plots = ttk.Frame(self.root)

        ttk.Label(flight_plots, text="Flight plots", font=self.HEADER_FONT) \
            .grid(row=0, column=0, sticky="w")

        tk.Frame(flight_plots, height=1, bg="grey") \
            .grid(row=1, column=0, sticky="ew", pady=5)

        fig = MFigure(figsize=(7, 4), facecolor='#ececec')
        fig.text(0.5, 0.01, 'Time [ms]', ha='center')
        fig.text(0.01, 0.5, 'Output', va='center', rotation='vertical')
        x_plot = fig.add_subplot(221)
        x_plot.grid()
        y_plot = fig.add_subplot(222)
        y_plot.grid()
        z_plot = fig.add_subplot(223)
        z_plot.grid()
        control_plot = fig.add_subplot(224)
        control_plot.grid()

        self.plots = [x_plot, y_plot, z_plot, control_plot]
        self.graph = MCanvas(fig, master=flight_plots)
        self.graph.get_tk_widget().grid(row=2, column=0, sticky="we")

        # Initialize random signal generator
        random_thread = threading.Thread(target=self.rand_data)
        random_thread.daemon = True
        random_thread.start()

        time.sleep(0.1)

        # Initialize plotter thread
        plotter_thread = threading.Thread(target=self.plotter)
        plotter_thread.daemon = True
        plotter_thread.start()

        # ----- GRID PLACEMENT -----
        top_menu.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        left_menu.grid(row=1, column=0, sticky="nw", padx=10)
        flight_plots.grid(row=1, column=1, sticky="nw", padx=10)

    def plotter(self):
        while self.engines_on:
            plot_data = self.signals.get_for_plotter()

            i = 1
            for p in self.plots:
                p.cla()
                p.grid()

                if not i == 7:
                    self.plot(p, plot_data[0], plot_data[i], plot_data[i + 1])
                else:
                    self.plot(p, plot_data[0], plot_data[i], None)

                i += 2

            time.sleep(1)

    def rand_data(self):
        t0 = time.time()
        time.sleep(0.03)

        while True:
            t = time.time() - t0
            self.signals.set_for_plotter(t, np.r_[randint(1, 5), randint(1, 5), randint(1, 5)], np.r_[3, 3, 3],
                                         randint(1, 5))

            time.sleep(0.03)

    @staticmethod
    def plot(fig, plot_time, measurement, reference=None):
        fig.plot(plot_time, measurement)

        # Set range for x axis (time)
        fig.set_xlim(min(plot_time), max(plot_time))
        ymin = min(measurement)
        ymax = max(measurement)

        if reference:
            fig.plot(plot_time, reference)
            ymin = min([ymin, min(reference)])
            ymax = max([ymax, max(reference)])

        ymin -= 10
        ymax += 10

        fig.set_ylim(ymin, ymax)
        fig.relim()

    def click(self, click_event):
        self.canvas_time_start = time.time()
        self.signals.set_canvas_xy_start(np.r_[click_event.x, click_event.y])
        self.prev_event = click_event

    def move(self, move_event):
        self.drawable_canvas.create_line(self.prev_event.x, self.prev_event.y, move_event.x, move_event.y, width=2)
        self.prev_event = move_event

        if self.canvas_time_start + 0.02 < time.time():
            self.signals.set_canvas_xy(np.r_[move_event.x, move_event.y])
            self.canvas_time_start = time.time()

    def clear_canvas(self, click_event):
        del click_event
        time.sleep(0.3)
        self.drawable_canvas.delete("all")
