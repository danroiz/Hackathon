import struct
import sys
import socket
import threading

dev_network = '172.01.255.255'
test_network = '172.99.255.255'
local_host = '127.0.0.1'
network_interface = local_host

# thread task for getting the game result from the server while waiting for answer from user
def get_game_result(tcp_sock):
    try:
        old_timeout = tcp_sock.gettimeout()
        tcp_sock.settimeout(20) # in case server doesn't resopond
        winner_msg = tcp_sock.recv(1024)
        tcp_sock.settimeout(old_timeout)
        print('\033[94m', winner_msg.decode("utf-8"), '\033[0m')
    except socket.error as e:
        print(e)
        print("Server doesn't respond after sending answer.")


class ClientNew:
    team_name = b'The Bitles\n'
    OFFERS_PORT = 13117
    BUFFER_SIZE = 1024

    def __init__(self):
        pass

    # main method for client 
    def start_client(self):
        while True:
            try:
                (server_ip, server_port) = self.get_offers()
                self.connect(server_ip, server_port)
            except Exception as e:
                print(e)

    def get_offers(self):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind((network_interface, self.OFFERS_PORT))
        print("Client started, listening for offer requests...")
        try:
            message, addr = udp_sock.recvfrom(self.BUFFER_SIZE)
        except socket.error as error:
            udp_sock.close()
            print("error getting offer from udp socket")
            raise error

        msg = struct.unpack('IbH', message)
        recv_magic_cookie = msg[0]
        self.verify_magic_cookie(recv_magic_cookie, udp_sock)
        recv_msg_type = msg[1]
        self.verify_type(recv_msg_type, udp_sock)
        server_port = msg[2]
        server_ip = addr[0]
        udp_sock.close()
        return server_ip, server_port

    def verify_type(self, recv_msg_type, udp_sock):
        offer_type = 0x2
        if recv_msg_type != offer_type:
            udp_sock.close()
            raise Exception("Bad offer type")

    def verify_magic_cookie(self, recv_magic_cookie, udp_sock):
        magic_cookie = 0xabcddcba
        if (magic_cookie != recv_magic_cookie):
            udp_sock.close()
            raise("Bad magic cookie :(")
            
    # connecting to server tcp socket as recived from the broadcast
    def connect(self, server_ip, server_port):
        print(f"\033[92mReceived offer from {server_ip}\nattempting to connect...\033[0m")
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_sock.connect((server_ip, server_port))
            tcp_sock.send(self.team_name)
            old_timeout = tcp_sock.gettimeout()
            tcp_sock.settimeout(30) # in case game won't start, abort game
            BUFFER_SIZE = 1024
            question = tcp_sock.recv(BUFFER_SIZE)
            tcp_sock.settimeout(old_timeout)
            print('\033[96m', question.decode("utf-8"), '\033[0m')
            get_game_result_thread = threading.Thread(target=get_game_result, args=(tcp_sock,))
            get_game_result_thread.start()
            ans = sys.stdin.readline()[0] # getting first char from user
            tcp_sock.send(bytearray(ans.encode()))
            get_game_result_thread.join() # wait incase we won but server didn't announced winner yet
        except socket.error as e:
            print(e)
        finally:
            print("Closing")
            tcp_sock.close()


if __name__ == '__main__':
    client = ClientNew()
    client.start_client()
