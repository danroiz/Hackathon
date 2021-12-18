import socket


class Client:
    def __init__(self):
        pass



    def run(self):
        offers_port = 13117
        buffer_size = 1024
        magic_cookie = bytearray.fromhex("abcddcba")
        print(magic_cookie)

        print("Client started, listening for offer requests...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', offers_port))

        def listen(self):
            message, addr = sock.recvfrom(buffer_size)
            recv_magic_cookie = message[0:4]
            for i in range(4):
                if magic_cookie[i] != recv_magic_cookie[i]:
                    return



        while(True):
            listen()



if __name__ == '__main__':
    Client().run()
