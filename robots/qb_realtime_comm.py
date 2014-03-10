import re
import sys
import time

import socket

class robosocket(socket.socket):
    def __init__(self, baseIP, robotIP, port):

        self.baseIP = baseIP
        self.robotIP = robotIP
        self.basePort = port
        self.robotPort = port
        if self.baseIP == self.robotIP: # Sorry, not enough computers
            self.basePort += 1

        #print("PC coordinates {}:{}".format(self.baseIP,self.basePort))
        #print("Robot coordinates {}:{}".format(self.robotIP,self.robotPort))

        self.replybuffer = ''

        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.settimeout(10.0) # ten seconds to make a connection
        try:
            self.bind((self.baseIP, self.basePort))
            self.settimeout(2.0)
            
        except socket.error as msg:
            print(msg)
            self.close()
            raise
              
    def sendtorobot(self,command):
        """Sends a command to the robot. The command will be delimited in accordance to the robot spec"""
        command = "${}*\n".format(command)
        if sys.version_info[0] == 3:
            command = command.encode("utf-8")
        i = 0
        while i < len(command):
            i += self.sendto(command[i:],(self.robotIP,self.robotPort))
        
    def recvreply(self):
        """Read reply from the robot, that is anything up to `\n`"""
        
        # I'm not sure what will actually happen if we timeout in the middle
        # of a reply (e.g. we read the first X characters, and then timeout)
        # The next read might be completely messed up
        
        while self.replybuffer.find('\n') < 0:
            try:
                line = self.recv(1024) #receives up to 1024 bytes
                if sys.version_info[0] == 3:
                    line = line.decode("utf-8")
            except socket.timeout as msg:
                print('Message not received, timeout')
                return None
            
            self.replybuffer += line

        i_n = self.replybuffer.find('\n')
        if i_n >= 0:
            reply = self.replybuffer[:i_n]
            self.replybuffer = self.replybuffer[(i_n+1):]
            return reply

        # Technically, unreachable code
        return None
        

class connection:
    def __init__(self, baseIP, robotIP, port):
        self.baseIP = baseIP
        self.robotIP = robotIP
        self.port = port
        self.comsocket = None
        
    def __enter__(self):
        if self.comsocket is None:
            self.comsocket = robosocket(self.baseIP, self.robotIP, self.port)       
        return self.comsocket
        
    def __exit__(self, exc_type, exc_value, traceback):
        # Shutdown always fails, because there is nothing connected at the other side
        #self.comsocket.shutdown(socket.SHUT_RDWR)
        try:
            self.comsocket.close()
            self.comsocket = None
        except Exception as e:
            print('Closing socket failed!')
            #raise
        return False
 
class qb_comm:
    """Communication class for quickbot communication.

    Low-level interface is unnecessary as high-level functions are available.

    Functions for the interface are:
    ==========================  ========================================================================
    ``qb_comm()``               creates the socket interface for PC to quickbot
    ``read()``                  low-low level udp socket communication, not needed except for extension
    ``write()``                 low-low level udp socket communication, not needed but for extension
    ``get_encoder_ticks()``     returns the encoder ticks ``(tl, tr)`` tuple
    ``get_encoder_velocity()``  returns the encoder velocities ``(vl, vr)`` tuple 
    ``get_ir_raw_values()``     returns the 5-tuple raw ADC values of the IR sensors
    ``set_speeds()``            sets the speed of the robot wheel velocities
    ``send_halt()``             sends the command to stop the quickbot velocitiy
    ``close()``                 the most essential command to call to close the interface
    ==========================  ========================================================================
    """
    def __init__(self, baseIP, robotIP, port):
        """Sets up the listening socket and generates regex comparison formatting."""
        #Setup IP address for UDP (datagram communication)
        self.baseIP = baseIP
        self.robotIP = robotIP
        self.port = port

        #efficient regex processing
        numpattern = '-?[0-9]*(?:\.[0-9]*)?' # matches some floating-point number
        self.rx_TWO = re.compile('\[(?P<LEFT>{0}), (?P<RIGHT>{0})\]'.format(numpattern))
        self.rx_IR = re.compile('\[({0}), ({0}), ({0}), ({0}), ({0})\]'.format(numpattern))

    def connect(self):       
        return connection(self.baseIP, self.robotIP, self.port)

    def send_halt(self):
        """Sends the command to stop the quickbot"""
        with self.connect() as connection:
            connection.sendtorobot('PWM=0,0')

    def send_reset(self):
        """Sends the command to stop the quickbot"""
        with self.connect() as connection:
            connection.sendtorobot('RESET')

    def set_pwm(self, l, r, connection):
        """Send the command to set the right and left motor velocities/PWM"""
        connection.sendtorobot( 'PWM={0},{1}'.format(int(l), int(r)) )

    def get_pwm(self, connection):
        """Sends the command to retrieve the right and left motor velocities. Returns a tuple of (vl, vr)"""
        connection.sendtorobot('PWM?')
        data = connection.recvreply()
        if data is not None:
            m = self.rx_TWO.match(data)
            if m is not None: #we get a match
                return float(m.group('LEFT')), float(m.group('RIGHT'))

        return None #default fail

    def get_encoder_ticks(self, connection):
        """Sends the command to retrieve the right and left encode values. Returns a tuple of (cl, cr)"""
        connection.sendtorobot('ENVAL?')
        data = connection.recvreply()
        if data is not None:
            m = self.rx_TWO.match(data)
            if m is not None: #we get a match
                return float(m.group('LEFT')), float(m.group('RIGHT'))

        return None #default fail
        
    def get_encoder_velocity(self, connection):
        """Sends the command to retrieve the right and left motor velocities. Returns a tuple of (vl, vr)"""
        connection.sendtorobot('ENVEL?')
        data = connection.recvreply()
        if data is not None:
            m = self.rx_TWO.match(data)
            if m is not None: #we get a match
                return float(m.group('LEFT')), float(m.group('RIGHT'))

        return None #default fail

    def get_ir_raw_values(self, connection):
        """Sends the command to retrieve the infrared sensors, returns 5-tuple sensor ADC values."""
        connection.sendtorobot('IRVAL?')
        data = connection.recvreply()
        if data is not None:
            m = self.rx_IR.match(data)
            if m is not None: #we get a match
                return list(map(float,m.groups()))

        return None #default fail

    def ping(self):
        with self.connect() as connection:
            connection.sendtorobot('CHECK')
            reply = connection.recvreply()
            print('Robot says "{}"'.format(reply))
            if reply is None or not len(reply):
                raise IOError("Robot not found")


