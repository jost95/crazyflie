from cflib import crazyflie, crtp


# GUI callback functions
def scan_nodes():
    available = crtp.scan_interfaces()
    radios = []

    if available:
        for i in available:
            radios.append(available[i][0])
    else:
        print('No Crazyflies found!')

    return radios


def connect_node():
    cf = crazyflie.Crazyflie(rw_cache='./cache')
    print('Connecting to', default_node.get())
    cf.open_link(default_node.get())