import socket
import sys
import threading
import time
from time import sleep

tcp_welcome_port = 1234
offers_port = 13117
udp_sock = 0


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


def get_answer(answer_arr, event, client):
    try:
        buffer_size = 1024
        msg = client.recv(buffer_size)
        answer_arr[0] = msg.decode("utf-8")
        answer_arr[1] = time.time()
        event.set()
    except Exception:
        return


def get_random_question():
    return "How much is 1+1?"


def run():
    buffer_size = 1024

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    tcp_welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_welcome_socket.bind((local_ip, tcp_welcome_port))
    tcp_welcome_socket.listen()

    stop_sending_offers = False
    print("Server started, listening on IP address", local_ip)
    # sending offers until 2 clients connected
    send_offers_thread = threading.Thread(target=send_offers, args=(lambda: stop_sending_offers,))
    send_offers_thread.start()
    client_connected_counter = 0
    clients = [None, None]  # each element is array of length 2 which containing client socket and client name
    while client_connected_counter < 2:
        (client, _) = tcp_welcome_socket.accept()  # blocking until some client connects
        clients[client_connected_counter] = [client, "MissChang"]
        client_connected_counter = client_connected_counter + 1
    tcp_welcome_socket.close()  # won't welcome more than 2 clients at a time
    stop_sending_offers = True  # stops the send_offers_thread thread from sending more offers

    FIRST_PLAYER = 0
    SECOND_PLAYER = 1
    SOCKET = 0
    NAME = 1

    for i in range(len(clients)):
        try:
            client_team_name = clients[i][0].recv(buffer_size)
            print("got name", client_team_name.decode("utf-8"))
            if client_team_name.decode("utf-8") == "":
                clients[i][NAME] = f'Anonymous Player {i}'
            else:
                clients[i][NAME] = (client_team_name.decode("utf-8"))
        except socket.error:
            print("Failed to obtain client", i, "team name.")
    sleep(10)
    reply = f'Welcome to Quick Maths.\nPlayer 1: {clients[0][1]}Player 2: {clients[1][1]}==\n' \
            f'Please answer the following question as fast as you can:\n{get_random_question()}?"'
    encoded_string = reply.encode()
    byte_array = bytearray(encoded_string)
    clients[FIRST_PLAYER][SOCKET].send(byte_array)
    clients[SECOND_PLAYER][SOCKET].send(byte_array)

    e = threading.Event()
    # create two threads with e as parameter
    # false means tie
    answers = [[None, None], [None, None]]
    t0 = threading.Thread(target=get_answer, args=(answers[0], e, clients[0][0],))
    t1 = threading.Thread(target=get_answer, args=(answers[1], e, clients[1][0],))
    t0.start()
    t1.start()

    ANSWER = 0
    TIME_ANSWERED = 1
    wait_return = e.wait(timeout=10)
    winner = clients[1][1]
    if wait_return:
        if answers[FIRST_PLAYER][ANSWER] != None:
            if answers[SECOND_PLAYER][ANSWER] != None:
                if answers[FIRST_PLAYER][TIME_ANSWERED] < answers[SECOND_PLAYER][TIME_ANSWERED]:
                    winner = clients[FIRST_PLAYER][NAME]
                else:
                    winner = clients[SECOND_PLAYER][NAME]
            else:
                winner = clients[FIRST_PLAYER][1]
        reply = f'Game over!\nThe correct answer was 4!\nCongratulations to the winner: {winner}'
        encoded_string = reply.encode()
        byte_array = bytearray(encoded_string)
        clients[0][0].send(byte_array)
        clients[1][0].send(byte_array)
    else:
        print("tie")
        reply = f'tie'
        encoded_string = reply.encode()
        byte_array = bytearray(encoded_string)
        clients[0][0].send(byte_array)
        clients[1][0].send(byte_array)

    print("close 0")
    clients[0][0].close()
    print("close 1")
    clients[1][0].close()


def start_server():
    try:
        while True:
            run()
    except socket.error:
        start_server()


class Server:
    def __init__(self):
        pass


if __name__ == '__main__':
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    start_server()
    udp_sock.close()
