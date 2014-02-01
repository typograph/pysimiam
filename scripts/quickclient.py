import socket

host = "mangerine.local"
port = 5005
class quickclient:
    def __init__(self):
        self.ssocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ssocket.settimeout(2.0)

        try:
            self.ssocket.bind((host, port))
        except socket.error as msg:
            print msg

    def read(self):
        try:
            data = self.ssocket.recv(1024)
            print data
        except socket.error as msg:
            print msg


    def send(self, msg):
        self.ssocket.send('what\'s up?')
        
        
