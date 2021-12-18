import socket
import struct
import sys
from time import sleep


def run():
    endian = sys.byteorder
    offers_port = 13117
    buffer_size = 1024
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")
    tcp_welcome_port = 12345
    tcp_welcome_port_bytes = tcp_welcome_port.to_bytes(2, endian)
    msg = bytearray()
    msg.extend(magic_cookie)
    msg.extend(offer_type)
    msg.extend(tcp_welcome_port_bytes)

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    print("Server started, listening on IP address", local_ip)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("my welcome port:", tcp_welcome_port)
    tcp_sock.bind((hostname, tcp_welcome_port))
    tcp_sock.listen(10)

    sending_offer = True
    while sending_offer:
        udp_sock.sendto(msg, ("255.255.255.255", offers_port))  # TODO:change to dynamic interface
        tcp_sock.accept()
        sleep(1)





class Server:
    def __init__(self):
        pass


if __name__ == '__main__':
    run()
