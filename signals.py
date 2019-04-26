import threading
import numpy as np
from collections import deque


def synchronized_with_attr(lock_name):
    def decorator(method):
        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

        return synced_method

    return decorator


class Signals:
    MAX_DATA_POINTS = 50

    def __init__(self):
        # Define our different locks
        self.cf_setup_lock = threading.RLock()
        self.control_lock = threading.RLock()
        self.ref_position_lock = threading.RLock()
        self.position_lock = threading.RLock()
        self.velocity_lock = threading.RLock()
        self.attitude_lock = threading.RLock()
        self.toggle_lock = threading.RLock()
        self.canvas_lock = threading.RLock()
        self.plotter_lock = threading.RLock()

        # Define shared variables
        self.__cf_setup = False
        self.__roll = 0.0
        self.__pitch = 0.0
        self.__yawrate = 0.0
        self.__thrust = 0
        self.__pos_ref = np.r_[0.0, 0.0, 0.0]
        self.__pos = np.r_[0.0, 0.0, 0.0]
        self.__vel = np.r_[0.0, 0.0, 0.0]
        self.__att = np.r_[0.0, 0.0, 0.0]
        self.__toggle_engines = False
        self.__canvas_xy_start = np.r_[0.0, 0.0]
        self.__canvas_xy = np.r_[0.0, 0.0]

        # For plotters
        self.__time_hist = deque(maxlen=30)
        self.__x_hist = deque(maxlen=30)
        self.__xref_hist = deque(maxlen=30)
        self.__y_hist = deque(maxlen=30)
        self.__yref_hist = deque(maxlen=30)
        self.__z_hist = deque(maxlen=30)
        self.__zref_hist = deque(maxlen=30)
        self.__thrust_hist = deque(maxlen=30)

    @synchronized_with_attr("canvas_lock")
    def set_canvas_xy_start(self, xy):
        self.__canvas_xy_start = xy
        self.__canvas_xy = xy

    @synchronized_with_attr("canvas_lock")
    def set_canvas_xy(self, xy):
        self.__canvas_xy = xy

    @synchronized_with_attr("canvas_lock")
    def get_canvas_diff(self):
        return self.__canvas_xy - self.__canvas_xy_start

    @synchronized_with_attr("cf_setup_lock")
    def set_cf_setup(self):
        self.__cf_setup = True

    @synchronized_with_attr("cf_setup_lock")
    def cf_setup(self):
        return self.__cf_setup

    @synchronized_with_attr("control_lock")
    def set_control(self, roll, pitch, yawrate, thrust):
        self.__roll = roll
        self.__pitch = pitch
        self.__yawrate = yawrate
        self.__thrust = int(thrust)

    @synchronized_with_attr("control_lock")
    def get_control(self):
        return self.__roll, self.__pitch, self.__yawrate, self.__thrust

    @synchronized_with_attr("ref_position_lock")
    def set_ref_position(self, pos_ref):
        self.__pos_ref = pos_ref

    @synchronized_with_attr("ref_position_lock")
    def set_xref_position(self, pos_ref):
        self.__pos_ref[0] = pos_ref

    @synchronized_with_attr("ref_position_lock")
    def set_yref_position(self, pos_ref):
        self.__pos_ref[1] = pos_ref

    @synchronized_with_attr("ref_position_lock")
    def set_zref_position(self, pos_ref):
        self.__pos_ref[2] = pos_ref

    @synchronized_with_attr("ref_position_lock")
    def get_ref_position(self):
        return self.__pos_ref

    @synchronized_with_attr("position_lock")
    def set_position(self, pos):
        self.__pos = pos

    @synchronized_with_attr("position_lock")
    def get_position(self):
        return self.__pos

    @synchronized_with_attr("velocity_lock")
    def set_velocity(self, pos):
        self.__pos = pos

    @synchronized_with_attr("velocity_lock")
    def get_velocity(self):
        return self.__pos

    @synchronized_with_attr("attitude_lock")
    def set_attitude(self, pos):
        self.__pos = pos

    @synchronized_with_attr("attitude_lock")
    def get_attitude(self):
        return self.__pos

    @synchronized_with_attr("toggle_lock")
    def read_toggle(self):
        return self.__toggle_engines

    @synchronized_with_attr("toggle_lock")
    def switch_toggle(self):
        self.__toggle_engines = not self.__toggle_engines

    @synchronized_with_attr("plotter_lock")
    def set_for_plotter(self, time, pos, pos_ref, thrust):
        self.__time_hist.append(time)
        self.__x_hist.append(pos[0])
        self.__xref_hist.append(pos_ref[0])
        self.__y_hist.append(pos[1])
        self.__yref_hist.append(pos_ref[1])
        self.__z_hist.append(pos[2])
        self.__zref_hist.append(pos_ref[2])
        self.__thrust_hist.append(thrust)

    @synchronized_with_attr("plotter_lock")
    def get_for_plotter(self):
        return self.__time_hist, self.__x_hist, self.__xref_hist, self.__y_hist, self.__yref_hist, self.__z_hist, \
               self.__zref_hist, self.__thrust_hist
