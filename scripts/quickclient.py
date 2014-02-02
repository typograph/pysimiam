import socket

host = "192.168.0.110"
target = "192.168.0.119"
port = 5005

class quickclient:
    def __init__(self):
        self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ssocket.settimeout(5.0)

        try:
            self.ssocket.bind((host, port)) # allavailable
        except socket.error as msg:
            print msg

    def read(self):
        try:
            data = self.ssocket.recv(1024)
            print data
        except socket.error as msg:
            print msg

    def write(self, command):
        self.ssocket.sendto(command, (target, port))

    def close(self):
        try:
            #self.ssocket.shutdown()
            self.ssocket.close()
        except socket.error as msg:
            print msg
