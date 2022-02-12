import os
import traceback
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from pythonosc import dispatcher, osc_server

SENSORS = ["TP9", "AF7", "AF8", "TP10", "AUX"]


def connect_data_steam(ip, port):
    routing_funcs = {
        "/muse/elements/horseshoe": headband_fit_handler,
        "/muse/eeg": eeg_handler,
        # "/muse/gyro": gyro_handler,
        # "/muse/acc": accelerator_handler,
    }
    data_handler = DataHandler(routing_funcs)

    dispatcher_ = dispatcher.Dispatcher()
    for routing_path in routing_funcs.keys():
        dispatcher_.map(routing_path, data_handler)

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher_)
    print(f"Listening on IP {ip} UDP port {port}")
    server.serve_forever()


class DataHandler:
    def __init__(self, routing_funcs):
        self.df = pd.DataFrame()
        self.routing_funcs = routing_funcs

    def update_data(self, data_item):
        data = pd.DataFrame.from_dict([data_item])
        self.df = pd.concat([self.df, data], ignore_index=True)
        print(data_item)

    def __call__(self, address: str, *args, **kwargs):
        timestamp = pd.Timestamp.now()
        func = self.routing_funcs[address]
        try:
            data = func(*args, **kwargs)
            data["timestamp"] = timestamp
            self.update_data(data)
            return data
        except Exception as err:
            traceback.print_exc()
            os._exit(0)


def eeg_handler(*raw_signal):
    # Streaming spec
    # https://mind-monitor.com/FAQ.php#oscspec
    data = {
        sensor_name: sensor_value
        for sensor_name, sensor_value in zip(SENSORS, raw_signal)
    }
    return data


def headband_fit_handler(*good_fits):
    fit_score = {1: "good", 2: "medium", 4: "bad"}
    data = {
        f"connection {sensor_name}": fit_score[sensor_value]
        for sensor_name, sensor_value in zip(SENSORS, good_fits)
    }
    return data


def gyro_handler(address: str, x, y, z):
    # print(x, y, z)
    print(f"GYROSCOPE: {x=},{y=},{z=}")


def accelerator_handler(address: str, x, y, z):
    # print(x, y, z)
    print(f"ACCELETOR: {x=},{y=},{z=}")
