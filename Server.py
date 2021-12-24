import socket
import sys
import threading
from time import sleep

tcp_welcome_port = 1234
offers_port = 13117


def send_offers(stop_offer):
    endian = sys.byteorder
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")
    tcp_welcome_port_bytes = tcp_welcome_port.to_bytes(2, endian)
    msg = bytearray()
    msg.extend(magic_cookie)
    msg.extend(offer_type)
    msg.extend(tcp_welcome_port_bytes)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    while not stop_offer():
        print("# Server sending broadcast")
        udp_sock.sendto(msg, ("255.255.255.255", offers_port))  # TODO:change to dynamic interface
        sleep(1)
    sleep(3)
    udp_sock.sendto(msg, ("255.255.255.255", offers_port))  # TODO:change to dynamic interface



def get_random_question():
    return "How much is 1+1?"


def run():
    buffer_size = 1024

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print("Server started, listening on IP address", local_ip)

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind((local_ip, tcp_welcome_port))
    tcp_sock.listen()
    to_stop = False
    t1 = threading.Thread(target=send_offers, args=(lambda: to_stop, ))
    t1.start()
    client_conncted = 0
    clients = [None, None]  # each element is array of length 2 which containing client socket and client name
    while client_conncted < 2:
        (client, _) = tcp_sock.accept()
        clients[client_conncted] = [client, ""]
        client_conncted = client_conncted + 1
        print("# SERVER CONNECTED TO:", client)
    tcp_sock.close()
    to_stop = True  # stops the t1 thread from sending more offers
    for i in range(len(clients)):
        msg = clients[i][0].recv(buffer_size)
        clients[i][1] = (msg.decode("utf-8"))
    sleep(10)
    reply = f'Welcome to Quick Maths.\nPlayer 1: {clients[0][1]}Player 2: {clients[1][1]}==\n' \
            f'Please answer the following question as fast as you can:\n{get_random_question()}?"'
    encoded_string = reply.encode()
    byte_array = bytearray(encoded_string)
    clients[0][0].send(byte_array)
    clients[1][0].send(byte_array)
    msg = clients[i][0].recv(buffer_size)
    print(msg)


class Server:
    def __init__(self):
        pass


if __name__ == '__main__':
    while True:
        run()
        print("# done")
