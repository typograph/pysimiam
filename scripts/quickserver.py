import socket
import re

baseIP = 'localhost'
robotIP = '192.168.0.7' # need to change this value for it to work
port = 5005

class quickserver:
    """Communication class for quickbot communication.

    Low-level interface is unnecessary as high-level functions are available.

    Functions for the interface are:
    ==========================  ========================================================================
    ``quickserver()``           creates the socket interface for PC to quickbot
    ``read()``                  low-low level udp socket communication, not needed except for extension
    ``write()``                 low-low level udp socket communication, not needed but for extension
    ``get_encoder_ticks()``     returns the encoder ticks ``(tl, tr)`` tuple
    ``get_encoder_velocity()``  returns the encoder velocities ``(vl, vr)`` tuple 
    ``get_ir_raw_values()``     returns the 5-tuple raw ADC values of the IR sensors
    ``set_speeds()``            sets the speed of the robot wheel velocities
    ``send_halt()``             sends the command to stop the quickbot velocitiy
    ``close()``                 the most essential command to call to close the interface
    ==========================  ========================================================================


    Specifically, the following variable is critical to setting the quickbot communication::
    =========== ===========
    ``robotIP`` 192.168.0.7
    =========== ===========

    """
    def __init__(self):
        """Sets up the listening socket (binds to port on robotIP) and generates regex comparison formatting."""
        #Setup IP address for UDP (datagram communication)
        self.baseIP = baseIP
        self.robotIP = robotIP
        self.port = port
        self.comsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.comsocket.settimeout(10.0) # ten seconds to make a connection

        #Set up for listening on host port
        try:
            self.comsocket.bind((baseIP, port))

            #if it works, shorten the delay time
            self.comsocket.settimeout(2.0)

        except socket.error as msg:
            print msg
            self.comsocket.close()

        #efficient regex processing
        pattern = '-?[0-9]*\.[0-9]*' # repeats twice for most things
        self.regex = re.compile(pattern)

    def write(self, command):
        """Write data in the `command` variable to the socket at a low level."""
        self.comsocket.sendto(command, (self.baseIP, self.port))

    def read(self):
        """Read data from the socket at low level"""
        #Need a try/catch to generate fail return (None object ref)
        try:
            line = self.robotSocket.recv(1024) #receives up to 1024 bytes
        except socket.error as msg:
            print 'Message not received, timeout'
            #Send a halt-message to avoid bumping into things
            self.send_halt()
            return None 

        return line #success

    def send_halt(self):
        """Sends the command to stop the quickbot"""
        self.write('$PWM=0.0,0.0*\n')

    def set_speeds(self, l, r): #same function name as JP
        """Send the command to set the right and left motor velocities/PWM"""
        s = '$PWM={0},{1}*\n'.format(l, r)
        self.write(s)

    def get_encoder_ticks(self):
        """Sends the command to retrieve the right and left motor velocities. Returns a tuple of (vl, vr)"""
        self.write('$ENVAL=?\n')
        data = self.read()
        if data is not None:
            res = self.regex.findall(data)
            if res is not None: #we get a match
                #important to check for more values than the two encoder data
                if len(res) == 2:                     
                    #map to a tuple of floats.
                    #the output format is (tl, tr) tuple
                    return tuple(map(float,res)) #a mouthful

        return None #default fail

        
    def get_encoder_velocity(self):
        """Sends the command to retrieve the right and left motor velocities. Returns a tuple of (vl, vr)"""
        self.write('$ENVEL=?\n')
        data = self.read()
        if data is not None:
            res = self.regex.findall(data)
            if res is not None: #we get a match
                #important to check for more values than just two encoder data 
                if len(res) == 2:                     
                    #map to a tuple of floats.
                    #the output format is (vl, vr) tuple
                    return tuple(map(float,res)) #a mouthful

        return None #default fail

    def get_ir_raw_values(self):
        """Sends the command to retrieve the infrared sensors, returns 5-tuple sensor ADC values."""
        self.write('$IRVAL=?*\n')
        data = self.read()
        if data is not None:
            res = self.regex.findall(data) #check __init__ for statement 
            if res is not None: #we get a match
                #important to check to ensure we are receiving ir data 
                # map to a tuple of floats.
                # the output format is (vl, vr) tuple
                if len(res) == 5: return tuple(map(lambda c: float(c),res))

        return None #default fail

    def close(self):
        """Close the socket--it's imperative to close the socket before closing program"""
        #Close socket
        try:
            self.send_halt() #stop the bot
            self.send_halt() #stop the bot, for good measure

            #Shutdown is not required, but network programmers frown when they don't see it.
            self.comsocket.shutdown()
            self.comsocket.close()
            self.comsocket = Null
        except socket.error as msg:
            print msg
