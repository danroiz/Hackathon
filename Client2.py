import array
import socket
import struct
import sys


def run():
    endian = '>H'
    if sys.byteorder == "little":
        endian = '<H'
    team_name = b'Dirty Bits\n'
    offers_port = 13117
    buffer_size = 1024
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")

    print("Client started, listening for offer requests...")

    def connect(dest_ip, dest_port):
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_sock.connect(('127.0.0.1', dest_port))
            print("Client connected successfully via TCP connection")
            tcp_sock.send(team_name)
            msg = tcp_sock.recv(1024)
            print(msg.decode("utf-8"))
            ans = sys.stdin.read(1)  # TODO: not blocking?
            tcp_sock.send(bytearray(ans.encode()))
            msg = tcp_sock.recv(1024)
            print(msg.decode("utf-8"))

        except Exception as e:
            print("connection failed", e)
        finally:
            print("Client closing TCP connection")
            tcp_sock.close()

    def listen():
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(('', offers_port))
        message, addr = udp_sock.recvfrom(buffer_size)
        recv_magic_cookie = message[0:4]
        for i in range(4):
            if magic_cookie[i] != recv_magic_cookie[i]:
                # print(message)
                return
        recv_msg_type = message[4]
        if recv_msg_type != offer_type[0]:
            # print(message)
            return
        server_port = struct.unpack(endian, message[5:7])[0]
        server_ip = addr
        udp_sock.close()
        connect(server_ip[0], server_port)

    while 1:
        print("Client listening")
        listen()


class Client:
    def __init__(self):
        pass


if __name__ == '__main__':
    run()
