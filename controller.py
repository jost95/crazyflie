import time
import threading
import numpy as np
from cflib.crazyflie.log import LogConfig
from cflib import crazyflie, crtp


class Controller(threading.Thread):
    def __init__(self, config, signals):
        super(Controller, self).__init__()

        crtp.init_drivers(enable_debug_driver=config["debug_driver"])
        self.cf = crazyflie.Crazyflie(rw_cache='./cache')

        # Inject crazyflie and set config parameters
        self.signals = signals
        self.start_time = time.time()
        self.gravity = config["gravity"]
        self.mass = config["mass"]
        self.period_in_ms = config["period_in_ms"]
        self.thrust_limit = config["thrust_limit"]
        self.roll_limit = config["roll_limit"]
        self.pitch_limit = config["pitch_limit"]
        self.yaw_limit = config["yaw_limit"]
        self.x_feedback = np.array(config["x_feedback"])
        self.y_feedback = np.array(config["y_feedback"])
        self.z_feedback = np.array(config["z_feedback"])
        self.thrust_scale = config["thrust_scale"]

        # Disable motors as default
        self.enabled = False

        # Connect some callbacks from the Crazyflie API
        self.cf.connected.add_callback(self._connected)
        self.cf.disconnected.add_callback(self._disconnected)
        self.cf.connection_failed.add_callback(self._connection_failed)
        self.cf.connection_lost.add_callback(self._connection_lost)
        self.send_setpoint = self.cf.commander.send_setpoint

        self.signals.set_cf_setup()

        # Exit when only thread alive
        self.daemon = True

    def get_cf(self):
        return self.cf

    def _connected(self, link_uri):
        print('Connected to', link_uri)

        log_stab_att = LogConfig(name='Stabilizer', period_in_ms=self.period_in_ms)
        log_stab_att.add_variable('stabilizer.roll', 'float')
        log_stab_att.add_variable('stabilizer.pitch', 'float')
        log_stab_att.add_variable('stabilizer.yaw', 'float')
        self.cf.log.add_config(log_stab_att)

        log_pos = LogConfig(name='Kalman Position', period_in_ms=self.period_in_ms)
        log_pos.add_variable('kalman.stateX', 'float')
        log_pos.add_variable('kalman.stateY', 'float')
        log_pos.add_variable('kalman.stateZ', 'float')
        self.cf.log.add_config(log_pos)

        log_vel = LogConfig(name='Kalman Velocity', period_in_ms=self.period_in_ms)
        log_vel.add_variable('kalman.statePX', 'float')
        log_vel.add_variable('kalman.statePY', 'float')
        log_vel.add_variable('kalman.statePZ', 'float')
        self.cf.log.add_config(log_vel)

        if log_stab_att.valid and log_pos.valid and log_vel.valid:
            log_stab_att.data_received_cb.add_callback(self._log_data_stab_att)
            log_stab_att.error_cb.add_callback(self._log_error)
            log_stab_att.start()

            log_pos.data_received_cb.add_callback(self._log_data_pos)
            log_pos.error_cb.add_callback(self._log_error)
            log_pos.start()

            log_vel.error_cb.add_callback(self._log_error)
            log_vel.data_received_cb.add_callback(self._log_data_vel)
            log_vel.start()
        else:
            raise RuntimeError('One or more of the variables in the configuration was not'
                               'found in log TOC. Will not get any position data.')

    @staticmethod
    def _connection_failed(link_uri, msg):
        print('Connection to %s failed: %s' % (link_uri, msg))

    @staticmethod
    def _connection_lost(link_uri, msg):
        print('Connection to %s lost: %s' % (link_uri, msg))

    @staticmethod
    def _disconnected(link_uri):
        print('Disconnected from %s' % link_uri)

    @staticmethod
    def _log_error(logconf, msg):
        print('Error when logging %s: %s' % (logconf.name, msg))

    def _log_data_stab_att(self, timestamp, data, logconf):
        del timestamp, logconf
        self.signals.set_attitude(np.r_[data['stabilizer.roll'], data['stabilizer.pitch'], data['stabilizer.yaw']])

    def _log_data_pos(self, timestamp, data, logconf):
        del timestamp, logconf
        self.signals.set_position(np.r_[data['kalman.stateX'], data['kalman.stateY'], data['kalman.stateZ']])

    def _log_data_vel(self, timestamp, data, logconf):
        del timestamp, logconf
        self.signals.set_velocity(np.r_[data['kalman.statePX'], data['kalman.statePY'], data['kalman.statePZ']])

    def reset_estimator(self):
        count = 0
        curr_pos = self.signals.get_position()

        # Position sanity check
        while not (np.max(np.abs(curr_pos[:2])) > 20 or curr_pos[2] < 0 or curr_pos[2] > 5) and count < 3:
            self.cf.param.set_value('kalman.resetEstimation', '1')
            time.sleep(0.1)
            self.cf.param.set_value('kalman.resetEstimation', '0')
            time.sleep(1.5)
            curr_pos = self.signals.get_position()
            count += 1

        if count == 3:
            raise RuntimeError('Position estimate out of bounds', curr_pos)

    def loop_sleep(self, time_start):
        delta_time = 1e-3 * self.period_in_ms - (time.time() - time_start)
        if delta_time > 0:
            time.sleep(delta_time)
        else:
            print('Deadline missed by', -delta_time, 'seconds. Too slow control loop!')

    def get_world_velocity(self, attitude):
        # Get angle in degrees
        roll, pitch, yaw = attitude * np.pi / 180

        rx = np.array([[1, 0, 0], [0, np.cos(roll), np.sin(roll)], [0, -np.sin(roll), np.cos(roll)]])
        ry = np.array([[np.cos(pitch), 0, -np.sin(pitch)], [0, 1, 0], [np.sin(pitch), 0, np.cos(pitch)]])
        rz = np.array([[np.cos(yaw), np.sin(yaw), 0], [-np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])

        return rx @ ry @ rz @ self.signals.get_velocity()

    @staticmethod
    def get_angle_control(feedback, e, v, limit):
        # Calculate state feedback control (from error in position and speed)
        u = np.dot(feedback, np.array([e, -v]).transpose())
        return np.clip(u, *limit)

    def get_thrust_control(self, e, v):
        # Calculate state feedback control (from error in position and speed)
        u_force = np.dot(self.z_feedback, np.array([e, -v]).transpose())

        # Adjust for gravity
        u_force += self.gravity * self.mass

        # Scale to thrust
        u_thrust = u_force * self.thrust_scale
        return np.clip(u_thrust, *self.thrust_limit)

    def canvas_adjust_reference(self, rx, ry):
        dx, dy = self.signals.get_canvas_diff()

        if not dx == 0:
            # Difference on screen normalized with canvas size and real area size
            fx = 1 - dx / 300 * 3
            fy = 1 + dy / 300 * 3
            rx *= fx
            ry *= fy

        return rx, ry

    def calc_control_signals(self):
        # Get measurement signals
        attitude = self.signals.get_attitude()
        vx, vy, vz = self.get_world_velocity(attitude)
        rx, ry, rz = self.signals.get_ref_position()
        x, y, z = self.signals.get_position()

        rx, ry = self.canvas_adjust_reference(rx, ry)

        ex = rx - x
        ey = ry - y
        ez = rz - z

        # Get control signals
        u_pitch = self.get_angle_control(self.x_feedback, ex, vx, self.pitch_limit)
        u_roll = self.get_angle_control(self.y_feedback, ey, vy, self.roll_limit)
        u_thrust = self.get_thrust_control(ez, vz)

        # Proportional adjustment of the yaw rate -> keep to zero to achieve decoupled system
        u_yawrate = np.clip(attitude[3], *self.yaw_limit)

        self.signals.set_ref_position(np.r_[rx, ry, rz])
        self.signals.set_control_signals(u_roll, u_pitch, u_yawrate, u_thrust)

    def run(self):
        # Wait for established connection
        while not self.cf.is_connected():
            time.sleep(0.2)

        print('Waiting for position estimate to be good enough...')
        self.reset_estimator()

        # Set the current reference to the current positional estimate
        self.signals.set_ref_position(self.signals.get_position())

        print('Initial positional reference:', self.signals.get_ref_position())

        while True:
            time_start = time.time()
            self.calc_control_signals()

            if self.signals.read_toggle():
                self.send_setpoint(0.0, 0.0, 0.0, 0)
                self.signals.set_control(0.0, 0.0, 0.0, 0)
                self.enabled = not self.enabled
                self.signals.switch_toggle()

            if self.enabled:
                self.send_setpoint(*self.signals.get_control_signals())

            self.loop_sleep(time_start)
