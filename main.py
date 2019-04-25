import controller as c
import application as app
import signals as s
import json
from cflib import crazyflie, crtp

if __name__ == "__main__":
    # Read default config
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Initialize shared signals class
    signals = s.Signals()

    # Initialize crazyflie
    crtp.init_drivers(enable_debug_driver=False)
    cf = crazyflie.Crazyflie(rw_cache='./cache')

    # Initialize controller
    control = c.Controller(cf, config, signals)
    control.start()

    # Initialize GUI and plotters
    app.Application(cf, signals)