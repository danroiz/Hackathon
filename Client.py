import socket
import struct
import sys


def run():
    offers_port = 13117
    buffer_size = 1024
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")

    print("Client started, listening for offer requests...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', offers_port))

    def connect(dest_ip, dest_port):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_sock.connect((dest_ip, dest_port))
        except Exception:
            print("connection failed")
        finally:
            tcp_sock.close()

    def listen():
        message, addr = sock.recvfrom(buffer_size)
        recv_magic_cookie = message[0:4]
        for i in range(4):
            if magic_cookie[i] != recv_magic_cookie[i]:
                return
        recv_msg_type = message[4]
        if recv_msg_type != offer_type[0]:
            return
        server_port = struct.unpack('>H', message[5:7])[0]
        server_ip = addr
        connect(server_ip, server_port)

    while 1:
        listen()


class Client:
    def __init__(self):
        pass


if __name__ == '__main__':
    run()
