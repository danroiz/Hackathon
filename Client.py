import socket
import struct
import sys


def run():
    endian = '>H'
    if sys.byteorder == "little":
        endian = '<H'

    offers_port = 13117
    buffer_size = 1024
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")

    print("Client started, listening for offer requests...")

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('', offers_port))

    def connect(dest_ip, dest_port):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print((dest_ip, dest_port))
            tcp_sock.connect((dest_ip, dest_port))
        except Exception as e:
            print("connection failed", e)
        finally:
            tcp_sock.close()

    def listen():
        message, addr = udp_sock.recvfrom(buffer_size)
        recv_magic_cookie = message[0:4]
        for i in range(4):
            if magic_cookie[i] != recv_magic_cookie[i]:
                print(message)
                return
        recv_msg_type = message[4]
        if recv_msg_type != offer_type[0]:
            print(message)
            return
        server_port = struct.unpack('<H', message[5:7])[0]
        server_ip = addr
        connect(server_ip[0], server_port)

    while 1:
        listen()


class Client:
    def __init__(self):
        pass


if __name__ == '__main__':
    run()
