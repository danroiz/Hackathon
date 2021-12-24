import socket
import struct
import sys


def run():
    endian = '>H'
    if sys.byteorder == "little":
        endian = '<H'
    team_name = b'The Bitles\n'
    offers_port = 13117
    buffer_size = 1024
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")

    def connect(destination_ip, destination_port):
        print("Received offer from", destination_ip, "\nattempting to connect...")
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.settimeout(15)
        try:

            tcp_sock.connect((destination_ip, destination_port))
            tcp_sock.send(team_name)
            print("BEFORE RECV")
            msg = tcp_sock.recv(1024)
            print("AFTER RECV")
            print(msg.decode("utf-8"))
            ans = sys.stdin.read(1)
            tcp_sock.send(bytearray(ans.encode()))
            try:
                msg = tcp_sock.recv(1024)
                print(msg.decode("utf-8"))
            except socket.error:
                print("Server doesn't respond after sending answer.")
        except socket.error as e:
            print("Server doesn't respond after connecting.")
        finally:
            tcp_sock.close()

    def listen():
        print("Client started, listening for offer requests...")
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
        server_ip = addr[0]
        udp_sock.close()
        connect(server_ip, server_port)

    while 1:
        listen()


class Client:
    def __init__(self):
        pass


if __name__ == '__main__':
    run()
