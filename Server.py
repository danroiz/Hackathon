import socket
import sys
import threading
# from time import sleep, time
import time
from scapy.all import *

DEV_NETWORK = 'eth1'
TEST_NETWORK = 'eth2'
BROADCAST_IP = '255.255.255.255'
DECODE_FORMAT = "utf-8"
# local_ip = get_if_addr(DEV_NETWORK)
local_ip = '127.0.0.1'

def send_offers_task(to_stop, tcp_port):
    # UDP SOCKET INIT
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.bind((local_ip, 0))
    offers_port = 13117
    endian = sys.byteorder
    magic_cookie = bytearray.fromhex("abcddcba")
    offer_type = bytearray.fromhex("02")
    tcp_welcome_port_bytes = tcp_port.to_bytes(2, endian)
    msg = bytearray()
    msg.extend(magic_cookie)
    msg.extend(offer_type)
    msg.extend(tcp_welcome_port_bytes)
    while not to_stop():
        print("# Server sending broadcast")
        udp_sock.sendto(msg, (BROADCAST_IP, offers_port))
        time.sleep(1)
    udp_sock.close()


def get_answer_from_player(player_socket, answer_arr, event):
    ANSWER = 0
    TIME_ANSWERED = 1
    BUFFER_SIZE = 1024
    TEN_SECOND = 10
    try:
        old_timeout = player_socket.gettimeout()
        player_socket.settimeout(TEN_SECOND)
        ans = player_socket.recv(BUFFER_SIZE)
        player_socket.settimeout(old_timeout)
        answer_arr[ANSWER] = ans.decode(DECODE_FORMAT)
        answer_arr[TIME_ANSWERED] = time.time()
        event.set()
    except socket.error as e:
        print("error getting answer from player", e)


class ServerNew:
    FIRST_PLAYER = 0
    SECOND_PLAYER = 1
    SOCKET = 0
    NAME = 1
    ANSWER = 0
    TIME_ANSWERED = 1
    TEN_SECOND = 10
    tcp_welcome_port = 2085
    BUFFER_SIZE = 1024
    udp_sock = 0

    def __init__(self):
        pass

    def start_server(self):
        
        while True:
            try:
                players, tcp_welcome_socket = self.send_offers_state()
                self.start_game(players)
                self.end_game(players)
            except socket.error as error:
                print("end", error)
            finally: 
                tcp_welcome_socket.close()

    def send_offers_state(self):
        # TCP WELCOME SOCKET INIT
        tcp_welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_welcome_socket.bind((local_ip, self.tcp_welcome_port))
        tcp_welcome_socket.listen()
        stop_sending_offers = False
        print("Server started, listening on IP address", local_ip)
        # sending offers until 2 clients connected
        send_offers_thread = \
            threading.Thread(target=send_offers_task, args=(lambda: stop_sending_offers, self.tcp_welcome_port,))
        send_offers_thread.start()
        # accept 2 clients
        client_connected_counter = 0
        players = [[None, None],
                   [None, None]]  # each element is array of length 2 which containing client socket and client name
        while client_connected_counter < 2:
            (client_socket, _) = tcp_welcome_socket.accept()  # blocking until some client connects
            players[client_connected_counter] = [client_socket, "Anonymous Player\n"]
            client_connected_counter = client_connected_counter + 1
            print("Player number", client_connected_counter, "has connected")
        # tcp_welcome_socket.close()  # won't welcome more than 2 clients at a time
        stop_sending_offers = True  # stops the send_offers_thread thread from sending more offers
        return players, tcp_welcome_socket

    def start_game(self, players):
        self.set_players_names(players)
        time.sleep(self.TEN_SECOND)
        question, answer = self.get_random_question()
        self.send_question(players, question)
        self.decide_winner(players, answer)

    def set_players_names(self, players):
        for i in range(len(players)):
            try:
                player_socket = players[i][self.SOCKET]
                old_timeout = player_socket.gettimeout()
                player_socket.settimeout(1)  # wait max 1 second for player to send his team name
                player_team_name = player_socket.recv(self.BUFFER_SIZE).decode(DECODE_FORMAT)
                player_socket.settimeout(old_timeout)
                players[i][self.NAME] = player_team_name
            except socket.error as error:
                print("error in set players name, player", i, error)

    def send_question(self, players, question):
        reply = f'Welcome to Quick Maths.\nPlayer 1: {players[self.FIRST_PLAYER][self.NAME]}' \
                f'Player 2: {players[self.SECOND_PLAYER][self.NAME]}==\n' \
                f'Please answer the following question as fast as you can:\n{question}'
        self.send_msg_to_players(players, reply)

    def get_random_question(self):
        operator = random.randint(0, 2)
        if operator == 0:
            return self.get_random_plus_question()
        elif operator == 1:
            return self.get_random_minus_question()
        else:
            return self.get_random_divide_question()

    def get_random_plus_question(self):
        answer = random.randint(0, 9)
        a = random.randint(0, answer)
        b = answer - a
        return f'How much is {a}+{b}?', answer

    def get_random_minus_question(self):
        answer = random.randint(0, 9)
        a = random.randint(answer, 100)
        b = a - answer
        return f'How much is {a}-{b}?', answer

    def get_random_divide_question(self):
        answer = random.randint(0, 9)
        a = random.randint(1, 10)
        b = answer * a
        return f'How much is {b}/{a}?', answer


    def send_msg_to_players(self, players, msg):
        encoded_string = msg.encode()
        byte_array = bytearray(encoded_string)
        try:
            players[self.FIRST_PLAYER][self.SOCKET].send(byte_array)
        except socket.error as error:
            print("error sending question to player 1", error)
            players[self.FIRST_PLAYER][self.SOCKET].close()
        try:
            players[self.SECOND_PLAYER][self.SOCKET].send(byte_array)
        except socket.error as error:
            players[self.SECOND_PLAYER][self.SOCKET].close()
            print("error sending question to player 2", error)

    def decide_winner(self, players, real_answer):
        event = threading.Event()
        answers = [[None, None], [None, None]]
        player1_get_ans_thread = threading.Thread(target=get_answer_from_player,
                                                  args=(players[self.FIRST_PLAYER][self.SOCKET], answers[self.FIRST_PLAYER], event,))
        player2_get_ans_thread = threading.Thread(target=get_answer_from_player,
                                                  args=(players[self.SECOND_PLAYER][self.SOCKET], answers[self.SECOND_PLAYER], event,))
        player1_get_ans_thread.start()
        player2_get_ans_thread.start()
        is_got_answer = event.wait(timeout=self.TEN_SECOND)  # if return false means tie
        print(is_got_answer)
        if is_got_answer:
            self.announce_winner(players, answers, real_answer)
        else:
            self.announce_tie(players, real_answer)

        try:
            players[self.FIRST_PLAYER][self.SOCKET].close()
            players[self.SECOND_PLAYER][self.SOCKET].close()
        except socket.error as error:
            print("error trying closing tcp sockets")
            print(error)
    
    def announce_winner(self, players, answers, real_answer):
        real_answer = str(real_answer)
        if answers[self.FIRST_PLAYER][self.ANSWER] is not None:
            if answers[self.SECOND_PLAYER][self.ANSWER] is not None:
                if answers[self.FIRST_PLAYER][self.TIME_ANSWERED] < answers[self.SECOND_PLAYER][self.TIME_ANSWERED]:
                    answer = answers[self.FIRST_PLAYER][self.ANSWER]
                    if answer == real_answer:
                        winner = players[self.FIRST_PLAYER][self.NAME]
                    else:
                        winner = players[self.SECOND_PLAYER][self.NAME]
                else:
                    answer = answers[self.SECOND_PLAYER][self.ANSWER]
                    if answer == real_answer:
                        winner = players[self.SECOND_PLAYER][self.NAME]
                    else:
                        winner = players[self.FIRST_PLAYER][self.NAME]

            else:
                answer = answers[self.FIRST_PLAYER][self.ANSWER]
                if answer == real_answer:
                    winner = players[self.FIRST_PLAYER][self.NAME]
                else:
                    winner = players[self.SECOND_PLAYER][self.NAME]
        else:
            answer = answers[self.SECOND_PLAYER][self.ANSWER]
            if answer == real_answer:
                winner = players[self.SECOND_PLAYER][self.NAME]
            else:
                winner = players[self.FIRST_PLAYER][self.NAME]
        winner_msg = f'Game over!\nThe correct answer was {real_answer}!\nCongratulations to the winner: {winner}'
        self.send_msg_to_players(players, winner_msg)

    def announce_tie(self, players, real_answer):
        tie_msg = f'Game over!\nThe correct answer was {real_answer}!\nDraw\n'
        self.send_msg_to_players(players, tie_msg)

    def end_game(self, players):
        players[self.FIRST_PLAYER][self.SOCKET].close()
        players[self.SECOND_PLAYER][self.SOCKET].close()


if __name__ == '__main__':
    server = ServerNew()
    server.start_server()
