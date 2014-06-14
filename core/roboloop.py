#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

"""The implementation of the simulator loop on the robot side.

   To be run on the robot.
"""

from time import time
import sys

from .pose import Pose

from robots.qb_embedded import QuickBot
#from robots.qb_realtime import QuickBot
from .helpers import Struct

import socket
from select import select

PAUSE = 0
RUN = 1
STOP = 2

class RoboLoop():
    """The RoboLoop runs QuickBot with a selected supervisor.
    
       It also runs a server on the specified port, and sets the parameters
       of the robot on external demand.

       :param port: The port on the robot to listen on,
       :type port: int
       :param supervisorclass: The class of the supervisor object to create,
       :type supervisorclass: class
    """

    def __init__(self, port, supervisorclass):
        """Create a simulator with *renderer* and *in_queue*
        """

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', port))
        self.server.listen(5)

        self.state = PAUSE
        
        self.robot = QuickBot(Pose())
#        self.robot = QuickBot(Pose(), options=Struct({'baseIP':'localhost',
                                                      #'robotIP':'localhost',
                                                      #'port':7777}))
        self.supervisor = supervisorclass(Pose(), self.robot.color, self.robot.info )

    def run(self):
        """Start the thread. In the loop there is an empty world with one robot."""

        log(self, 'starting main loop')

        self.time = time()        

        while self.state != STOP:

            self.robot.update_external_info()

            if self.state != PAUSE:
                new_time = time()
                inputs = self.supervisor.execute(self.robot.get_info(), new_time - self.time)
                self.time = new_time

                self.robot.set_inputs(inputs)
            
            if select([self.server],[],[],0)[0]:
                self.process_request(*self.server.accept())

    def process_request(self, client, addr):
        cmd = ""
        
        # Read the command
        while True:
            sbuffer = client.recv(1024)
            if not sbuffer:
                break
            cmd += sbuffer.decode('utf-8')
            
        print(cmd)
        
        # Process the command
        if cmd == "UI?":
            client.sendall(repr(self.supervisor.get_ui_description()).encode('utf-8'))
        elif cmd == "PARAM?":
            client.sendall(repr(self.supervisor.get_parameters()).encode('utf-8'))
        elif cmd.startswith("PARAM="):
            self.supervisor.set_parameters(Struct(cmd[6:]))
        elif cmd == "STOP":
            self.state = STOP
        elif cmd == "PAUSE":
            self.state = PAUSE
            self.robot.pause()
        elif cmd == "RUN":
            self.state = RUN
            self.robot.resume()
        else:
            log(self, "Command {} not recognized".format(cmd))
            
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    def log(self, msg):
        print(msg)
    
#end class RoboLoop

