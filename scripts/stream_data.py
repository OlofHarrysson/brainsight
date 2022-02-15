import socket

from brainsight.data_receiving import data_handling


def stream_data():
    # ip = "192.168.68.111"
    port = 5000
    ip = get_ip_address()  # IP to laptop
    data_handling.connect_data_steam(ip, port)


def get_ip_address():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    return sock.getsockname()[0]


if __name__ == "__main__":
    stream_data()
