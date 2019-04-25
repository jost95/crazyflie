import tkinter as tk
import tkinter.ttk as ttk
import time
import matplotlib

from cflib import crtp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as MCanvas
from matplotlib.figure import Figure as MFigure
from matplotlib import style as mstyle

mstyle.use('ggplot')
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
            self.connect_btn['state'] = 'disabled'

    def toggle_connection(self):
        if self.connected:
            self.cf.close_link()
            self.scan_btn['state'] = 'normal'
            self.connect_btn['state'] = 'disabled'
            self.engines_btn['state'] = 'disabled'
            self.connect_btn_text.set("Connect")
            self.engines_btn_text.set("Start engines")
        else:
            self.cf.open_link(self.selected_radio.get())
            self.scan_btn['state'] = 'disabled'
            self.engines_btn['state'] = 'normal'
            self.connect_btn_text.set("Disconnect")

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
        self.signals.set_zref_position(self.z_ref_entry.get())

    def __init__(self, root, cf, signals):
        super(Application, self).__init__()

        self.root = root
        self.cf = cf
        self.signals = signals

        self.connected = False
        self.engines_on = False

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

        self.drawable_canvas = tk.Canvas(left_menu, height=300, bg='#ECECEC')
        self.drawable_canvas.grid(row=8, column=0, columnspan=4, sticky="we", pady=5)
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
        y_plot = fig.add_subplot(222)
        z_plot = fig.add_subplot(223)
        control_plot = fig.add_subplot(224)

        graph = MCanvas(fig, master=flight_plots)
        graph.get_tk_widget().grid(row=2, column=0, sticky="we")

        # ----- GRID PLACEMENT -----
        top_menu.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        left_menu.grid(row=1, column=0, sticky="nw", padx=10)
        flight_plots.grid(row=1, column=1, sticky="nw", padx=10)

    def click(self, click_event):
        self.prev_event = click_event

    def move(self, move_event):
        self.drawable_canvas.create_line(self.prev_event.x, self.prev_event.y, move_event.x, move_event.y, width=2)
        self.prev_event = move_event

    def clear_canvas(self, click_event):
        time.sleep(0.3)
        del click_event
        self.drawable_canvas.delete("all")
