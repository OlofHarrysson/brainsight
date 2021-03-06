import os
import traceback
from pathlib import Path

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

    # server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher_) # Race conditions
    server = osc_server.BlockingOSCUDPServer((ip, port), dispatcher_)
    print(f"Listening on IP {ip} UDP port {port}")
    server.serve_forever()


class DataHandler:
    # TODO: Try to stream directly to dashboard
    def __init__(self, routing_funcs):
        self.routing_funcs = routing_funcs
        self.index_file = Path("output") / "meta.csv"
        self.index_file.unlink(missing_ok=True)
        self.nbr_warmup_items = 50
        self.columns = set()
        self.data_header = pd.DataFrame([], columns=list(self.columns))

    def create_header(self, data_item):
        # Gather the data columns for the first iterations

        if self.columns:  # If header already been created
            return True

        self.nbr_warmup_items -= 1
        data_item = pd.DataFrame.from_dict([data_item])
        self.data_header = pd.concat([self.data_header, data_item], ignore_index=True)

        if self.nbr_warmup_items == 0:
            self.columns = set(self.data_header.columns)
            self.data_header = pd.DataFrame([], columns=list(self.columns))
            self.data_header = self.data_header.sort_index(axis=1)
            col = self.data_header.pop("timestamp")
            self.data_header.insert(0, col.name, col)
            self.data_header.to_csv(self.index_file, mode="a", index=False, header=True)

        return self.nbr_warmup_items == 0

    def update_data(self, data_item):
        data_item = pd.DataFrame.from_dict([data_item])
        data_row = pd.concat([self.data_header, data_item], ignore_index=True)
        data_row.to_csv(self.index_file, mode="a", index=False, header=False)
        # print(data_item)

    def __call__(self, address: str, *args, **kwargs):
        timestamp = pd.Timestamp.now()
        func = self.routing_funcs[address]
        try:
            data = func(*args, **kwargs)
            data["timestamp"] = timestamp
            if self.create_header(data):
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
