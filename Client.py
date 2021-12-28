import struct
import sys
import socket
import threading
from scapy.all import *

dev_network = 'eth1'
test_network = 'eth2'
local_ip = get_if_addr(dev_network)

def get_game_result(tcp_sock):
    try:
        old_timeout = tcp_sock.gettimeout()
        tcp_sock.settimeout(20)
        winner_msg = tcp_sock.recv(1024)
        tcp_sock.settimeout(old_timeout)
        print(winner_msg.decode("utf-8"))
    except socket.error as e:
        print(e)
        print("Server doesn't respond after sending answer.")


class ClientNew:
    team_name = b'The Bitles\n'
    OFFERS_PORT = 13117
    BUFFER_SIZE = 1024

    def __init__(self):
        pass

    def start_client(self):
        while True:
            try:
                (server_ip, server_port) = self.get_offers()
                print("server ip", server_ip)
                print("server port", server_port)
                self.connect(server_ip, server_port)
            except Exception as e:
                print(e)

    def get_offers(self):
        endian = '>H'
        if sys.byteorder == "little":
            endian = '<H'
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(('', self.OFFERS_PORT))
        print("Client started, listening for offer requests...")
        try:
            message, addr = udp_sock.recvfrom(self.BUFFER_SIZE)
            print("got message", message)
        except socket.error as error:
            udp_sock.close()
            print("error getting offer from udp socket")
            raise error
        self.verify_msg(message, udp_sock)
        server_port = struct.unpack(endian, message[5:7])[0] #*********************
        server_ip = addr[0]
        udp_sock.close()
        return server_ip, server_port

    def verify_msg(self, message, udp_sock):
        magic_cookie = bytearray.fromhex("abcddcba")
        offer_type = bytearray.fromhex("02")
        recv_magic_cookie = message[0:4]
        for i in range(4):
            if magic_cookie[i] != recv_magic_cookie[i]:
                udp_sock.close()
                raise Exception("Bad magic cookie")
        recv_msg_type = message[4]
        if recv_msg_type != offer_type[0]:
            udp_sock.close()
            raise Exception("Bad offer type")

    def connect(self, server_ip, server_port):
        # server_ip = "169.254.44.73"  # TODO: erase this
        print("Received offer from", server_ip, "\nattempting to connect...")
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_sock.connect((server_ip, server_port))
            tcp_sock.send(self.team_name)
            old_timeout = tcp_sock.gettimeout()
            tcp_sock.settimeout(30)
            question = tcp_sock.recv(1024)
            tcp_sock.settimeout(old_timeout)
            print(question.decode("utf-8"))
            t1 = threading.Thread(target=get_game_result, args=(tcp_sock,))
            t1.start()
            ans = sys.stdin.readline()
            tcp_sock.send(bytearray(ans.encode()))
            t1.join()
        except socket.error as e:
            print(e)
        finally:
            print("Closing")
            tcp_sock.close()


if __name__ == '__main__':
    client = ClientNew()
    client.start_client()
