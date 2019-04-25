import numpy as np


def synchronized_with_attr(lock_name):
    def decorator(method):
        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

        return synced_method

    return decorator


class Signals:
    def __init__(self):
        self.__roll = 0.0
        self.__pitch = 0.0
        self.__yawrate = 0.0
        self.__thrust = 0
        self.__pos_ref = np.r_[0.0, 0.0, 0.0]
        self.__pos = np.r_[0.0, 0.0, 0.0]
        self.__vel = np.r_[0.0, 0.0, 0.0]
        self.__att = np.r_[0.0, 0.0, 0.0]
        self.__toggle_engines = False

    @synchronized_with_attr("control")
    def set_control(self, roll, pitch, yawrate, thrust):
        self.__roll = roll
        self.__pitch = pitch
        self.__yawrate = yawrate
        self.__thrust = int(thrust)

    @synchronized_with_attr("control")
    def get_control(self):
        return self.__roll, self.__pitch, self.__yawrate, self.__thrust

    @synchronized_with_attr("ref_position")
    def set_ref_position(self, pos_ref):
        self.__pos_ref = pos_ref

    @synchronized_with_attr("ref_position")
    def set_xref_position(self, pos_ref):
        self.__pos_ref[0] = pos_ref

    @synchronized_with_attr("ref_position")
    def set_yref_position(self, pos_ref):
        self.__pos_ref[1] = pos_ref

    @synchronized_with_attr("ref_position")
    def set_zref_position(self, pos_ref):
        self.__pos_ref[2] = pos_ref

    @synchronized_with_attr("ref_position")
    def get_ref_position(self):
        return self.__pos_ref

    @synchronized_with_attr("position")
    def set_position(self, pos):
        self.__pos = pos

    @synchronized_with_attr("position")
    def get_position(self):
        return self.__pos

    @synchronized_with_attr("velocity")
    def set_velocity(self, pos):
        self.__pos = pos

    @synchronized_with_attr("velocity")
    def get_velocity(self):
        return self.__pos

    @synchronized_with_attr("attitude")
    def set_attitude(self, pos):
        self.__pos = pos

    @synchronized_with_attr("attitude")
    def get_attitude(self):
        return self.__pos

    @synchronized_with_attr("toggle")
    def read_toggle(self):
        return self.__toggle_engines

    @synchronized_with_attr("toggle")
    def switch_toggle(self):
        self.__toggle_engines = not self.__toggle_engines
