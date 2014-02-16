#
# (c) PySimiam Team 2014
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
import numpy as np
from pose import Pose
from sensor import ProximitySensor
from robot import SimBot as Robot
from math import ceil, exp, sin, cos, tan, pi, copysign
from helpers import Struct
import socket
import sys
import re

class QuickBot_IRSensor(ProximitySensor):
    """Inherits from the proximity sensor class. Performs calculations specific to the khepera3 for its characterized proximity sensors"""
    
    ir_coeff = np.array([ 1.16931064e+07,  -1.49425626e+07, \
                          7.96904053e+06,  -2.28884314e+06, \
                          3.80068213e+05,  -3.64435691e+04, \
                          1.89558821e+03])
    
    def __init__(self,pose,robot):
        # values copied from SimIAm    
        ProximitySensor.__init__(self, pose, robot, (0.04, 0.3, np.radians(6)))

    def distance_to_value(self,dst):
        """Returns the distance calculation from the distance readings of the proximity sensors""" 
        
        if dst < self.rmin :
            return 917
        elif dst > self.rmax:
            return 133
        else:
            return int(np.polyval(self.ir_coeff,dst))

class QuickBot(Robot):
    """Emulates a standalone QuickBot. Will not listen to the local supervisor.""" 
    
    beta = (0.0425, -0.9504)
    
    def __init__(self, pose, color = 0xFFFFFF, options = None):
        Robot.__init__(self, pose, color)
        
        # create shape
        self._shapes = Struct()
        
        self._shapes.base_plate = np.array([[ 0.0335, 0.0534, 1],
                                            [ 0.0429, 0.0534, 1],
                                            [ 0.0639, 0.0334, 1],
                                            [ 0.0686, 0.0000, 1],
                                            [ 0.0639,-0.0334, 1],
                                            [ 0.0429,-0.0534, 1],
                                            [ 0.0335,-0.0534, 1],
                                            [-0.0465,-0.0534, 1],
                                            [-0.0815,-0.0534, 1],
                                            [-0.1112,-0.0387, 1],
                                            [-0.1112, 0.0387, 1],
                                            [-0.0815, 0.0534, 1],
                                            [-0.0465, 0.0534, 1]])
                         
        self._shapes.bbb = np.array([[-0.0914,-0.0406, 1],
                                    [-0.0944,-0.0376, 1],
                                    [-0.0944, 0.0376, 1],
                                    [-0.0914, 0.0406, 1],
                                    [-0.0429, 0.0406, 1],
                                    [-0.0399, 0.0376, 1],
                                    [-0.0399,-0.0376, 1],
                                    [-0.0429,-0.0406, 1]])
                    
        self._shapes.bbb_rail_l = np.array([[-0.0429, -0.0356,1],
                                            [-0.0429, 0.0233,1],
                                            [-0.0479, 0.0233,1],
                                            [-0.0479,-0.0356,1]])
                          
        self._shapes.bbb_rail_r = np.array([[-0.0914,-0.0356,1],
                                            [-0.0914, 0.0233,1],
                                            [-0.0864, 0.0233,1],
                                            [-0.0864,-0.0356,1]])
                          
        self._shapes.bbb_eth = np.array([[-0.0579, 0.0436, 1],
                                         [-0.0579, 0.0226, 1],
                                         [-0.0739, 0.0226, 1],
                                         [-0.0739, 0.0436, 1]])
                       
        self._shapes.left_wheel = np.array([[ 0.0254, 0.0595, 1],
                                            [ 0.0254, 0.0335, 1],
                                            [-0.0384, 0.0335, 1],
                                            [-0.0384, 0.0595, 1]])
                          
        self._shapes.left_wheel_ol = np.array([[ 0.0254, 0.0595, 1],
                                               [ 0.0254, 0.0335, 1],
                                               [-0.0384, 0.0335, 1],
                                               [-0.0384, 0.0595, 1]])
            
        self._shapes.right_wheel_ol = np.array([[ 0.0254,-0.0595, 1],
                                                [ 0.0254,-0.0335, 1],
                                                [-0.0384,-0.0335, 1],
                                                [-0.0384,-0.0595, 1]])
                         
        self._shapes.right_wheel = np.array([[ 0.0254,-0.0595, 1],
                                             [ 0.0254,-0.0335, 1],
                                             [-0.0384,-0.0335, 1],
                                             [-0.0384,-0.0595, 1]])
                         
        self._shapes.ir_1 = np.array([[-0.0732, 0.0534, 1],
                                      [-0.0732, 0.0634, 1],
                                      [-0.0432, 0.0634, 1],
                                      [-0.0432, 0.0534, 1]])
                    
        self._shapes.ir_2 = np.array([[ 0.0643, 0.0214, 1],
                                      [ 0.0714, 0.0285, 1],
                                      [ 0.0502, 0.0497, 1],
                                      [ 0.0431, 0.0426, 1]])
                    
        self._shapes.ir_3 = np.array([[ 0.0636,-0.0042, 1],
                                      [ 0.0636, 0.0258, 1],
                                      [ 0.0736, 0.0258, 1],
                                      [ 0.0736,-0.0042, 1]])
                    
        self._shapes.ir_4 = np.array([[ 0.0643,-0.0214, 1],
                                      [ 0.0714,-0.0285, 1],
                                      [ 0.0502,-0.0497, 1],
                                      [ 0.0431,-0.0426, 1]])
                    
        self._shapes.ir_5 = np.array([[-0.0732,-0.0534, 1],
                                      [-0.0732,-0.0634, 1],
                                      [-0.0432,-0.0634, 1],
                                      [-0.0432,-0.0534, 1]])

        self._shapes.bbb_usb = np.array([[-0.0824,-0.0418, 1],
                                         [-0.0694,-0.0418, 1],
                                         [-0.0694,-0.0278, 1],
                                         [-0.0824,-0.0278, 1]])
        
        # create IR sensors
        self.ir_sensors = []
              
        ir_sensor_poses = [
                          Pose(-0.0474, 0.0534, np.radians(90)),
                          Pose( 0.0613, 0.0244, np.radians(45)),
                          Pose( 0.0636, 0.0, np.radians(0)),
                          Pose( 0.0461,-0.0396, np.radians(-45)),
                          Pose(-0.0690,-0.0534, np.radians(-90))
                          ]                          
                           
        for pose in ir_sensor_poses:
            self.ir_sensors.append(QuickBot_IRSensor(pose,self))
                                
        # initialize motion
        self.ang_velocity = (0.0,0.0)

        self.info = Struct()
        self.info.wheels = Struct()
        # these were the original parameters
        self.info.wheels.radius = 0.0325
        self.info.wheels.base_length = 0.09925
        self.info.wheels.ticks_per_rev = 16.0
        self.info.wheels.left_ticks = 0
        self.info.wheels.right_ticks = 0
        
        self.info.wheels.max_velocity = 2*pi*130/60 # 130 RPM
        self.info.wheels.min_velocity = 2*pi*30/60  #  30 RPM
        
        self.left_revolutions = 0.0
        self.right_revolutions = 0.0
        
        self.info.ir_sensors = Struct()
        self.info.ir_sensors.poses = ir_sensor_poses
        self.info.ir_sensors.readings = None
        self.info.ir_sensors.rmax = 0.3
        self.info.ir_sensors.rmin = 0.04

        # Time to get online

        if options is None:
            self.baseIP = 'localhost'
            self.robotIP = 'localhost'
            self.basePort = 5005
            self.robotPort = 5005
        else:
            self.baseIP = options.baseIP
            self.robotIP = options.robotIP
            self.basePort = options.port
            self.robotPort = options.port

        # Sorry, not enough computers
        if self.baseIP == self.robotIP:
            self.basePort += 1
        
        print("PC coordinates {}:{}".format(self.baseIP,self.basePort))
        print("Robot coordinates {}:{}".format(self.robotIP,self.robotPort))
                    
        self.robotSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.robotSocket.setblocking(False)
        
        # As always, not a terribly good idea, but it's only a test
        self.robotSocket.bind((self.robotIP, self.robotPort))
        # The socket will close in the destructor. No idea when that will be.
        
        self.cmdBuffer = ''

    def draw(self,r):
        r.set_pose(self.get_pose())
        r.set_pen(0)
        r.set_brush(0)
        r.draw_polygon(self._shapes.ir_1)
        r.draw_polygon(self._shapes.ir_2)
        r.draw_polygon(self._shapes.ir_3)
        r.draw_polygon(self._shapes.ir_4)
        r.draw_polygon(self._shapes.ir_5)
        
        r.draw_polygon(self._shapes.left_wheel)
        r.draw_polygon(self._shapes.right_wheel)
        
        r.set_pen(0x01000000)
        r.set_brush(self.get_color())
        r.draw_polygon(self._shapes.base_plate)

        r.set_pen(0x10000000)
        r.set_brush(None)
        r.draw_polygon(self._shapes.left_wheel)
        r.draw_polygon(self._shapes.right_wheel)        
        
        r.set_pen(None)
        r.set_brush(0x333333)
        r.draw_polygon(self._shapes.bbb)
        r.set_brush(0)
        r.draw_polygon(self._shapes.bbb_rail_l)
        r.draw_polygon(self._shapes.bbb_rail_r)
        r.set_brush(0xb2b2b2)
        r.draw_polygon(self._shapes.bbb_eth)
        r.draw_polygon(self._shapes.bbb_usb)
        
    def get_envelope(self):
        return self._shapes.base_plate
    
    def move(self,dt):
        # There's no need to use the integrator - these equations have a solution        
        (vl, vr) = self.get_wheel_speeds()
        (v,w) = self.diff2uni((vl,vr))
        x, y, theta = self.get_pose()
        if w == 0:
            x += v*cos(theta)*dt
            y += v*sin(theta)*dt
        else:
            dtheta = w*dt
            x += 2*v/w*cos(theta + dtheta/2)*sin(dtheta/2)
            y += 2*v/w*sin(theta + dtheta/2)*sin(dtheta/2)
            theta += dtheta
        
        self.set_pose(Pose(x, y, (theta + pi)%(2*pi) - pi))

        self.left_revolutions += vl*dt/2/pi
        self.right_revolutions += vr*dt/2/pi
        self.info.wheels.left_ticks = int(self.left_revolutions*self.info.wheels.ticks_per_rev)
        self.info.wheels.right_ticks = int(self.right_revolutions*self.info.wheels.ticks_per_rev)
        
        # Time to see what they want from us
        self.parseCmdBuffer()
        
    def get_info(self):
        self.info.ir_sensors.readings = [sensor.reading() for sensor in self.ir_sensors]
        return self.info
    
    def set_inputs(self,inputs):
        # IGNORE INPUTS. This is an autonomous bot.
        pass
    
    def diff2uni(self,diff):
        (vl,vr) = diff
        v = (vl+vr) * self.info.wheels.radius/2;
        w = (vr-vl) * self.info.wheels.radius/self.info.wheels.base_length;
        return (v,w)

    def v2pwm(self,vl,vr):
        """Convert from angular velocity to PWM"""
        if vl == 0 and vr == 0:
            return 0,0
        
        # Shamelessly copied from SimIAm.
        # The formulae seem strange       
        pwm_l = copysign((abs(vl/(2*pi)) - self.beta[1])/self.beta[0], vl);
        pwm_r = copysign((abs(vr/(2*pi)) - self.beta[1])/self.beta[0], vr);

        return max(min(round(pwm_l), 100), -100), \
               max(min(round(pwm_r), 100), -100)
    
    def pwm2v(self,pwm_l,pwm_r):
        """Convert from PWM to angular velocity"""

        if pwm_l == 0 and pwm_r == 0:
            return 0,0
        # This will fail horribly for funny PWM
        
        
        #if abs(pwm_l) > 130:
            #pwm_l = copysign(130,pwm_l)
        #if abs(pwm_l) < 40:
            #vl = 0
        #else:
        vl = 2*pi*copysign(1,pwm_l)*(self.beta[0]*abs(pwm_l) + self.beta[1])
            
        #if abs(pwm_r) > 130:
            #pwm_r = copysign(130,pwm_r)
        #if abs(pwm_l) < 40:
            #vr = 0
        #else:
        vr = 2*pi*copysign(1,pwm_r)*(self.beta[0]*abs(pwm_r) + self.beta[1])
        
        return vl, vr
    
    def get_wheel_speeds(self):
        return self.ang_velocity
    
    def set_pwm(self, pwm_l, pwm_r):
        self.ang_velocity = self.pwm2v(pwm_l, pwm_r)

    def get_external_sensors(self):
        return self.ir_sensors

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        for sensor in self.ir_sensors:
            sensor.draw(renderer)
            
    def update_sensors(self):
        for sensor in self.ir_sensors:
            sensor.update_distance()

    def parseCmdBuffer(self):
        def sendtobase(message):
            #print('Sending ' + message)
            message += '\n'
            if sys.version_info.major == 3:
                message = message.encode('utf-8')
            self.robotSocket.sendto(message,(self.baseIP, self.basePort))

        try:
            line = self.robotSocket.recv(1024)
        except socket.error as msg:
            return
        
        if sys.version_info.major == 3:
            line = line.decode('utf-8')

        self.cmdBuffer += line

        bufferPattern = r'\$[^\$\*]*?\*' # String contained within $ and * symbols with no $ or * symbols in it
        bufferRegex = re.compile(bufferPattern)
        bufferResult = bufferRegex.search(self.cmdBuffer)

        if bufferResult:
            msg = bufferResult.group()
            #print(msg)
            self.cmdBuffer = ''

            msgPattern = r'\$(?P<CMD>[A-Z]{3,})(?P<SET>=?)(?P<QUERY>\??)(?(2)(?P<ARGS>.*)).*\*'
            msgRegex = re.compile(msgPattern)
            msgResult = msgRegex.search(msg)

            if msgResult.group('CMD') == 'CHECK':
                sendtobase('Hello from QuickBot')

            elif msgResult.group('CMD') == 'PWM':
                if msgResult.group('QUERY'):
                    sendtobase('[{}, {}]'.format(*self.v2pwm(*self.ang_velocity)))

                elif msgResult.group('SET') and msgResult.group('ARGS'):
                    args = msgResult.group('ARGS')
                    pwmArgPattern = r'(?P<LEFT>[-]?\d+),(?P<RIGHT>[-]?\d+)'
                    pwmRegex = re.compile(pwmArgPattern)
                    pwmResult = pwmRegex.match(args)
                    if pwmResult:
                        self.set_pwm(int(pwmRegex.match(args).group('LEFT')), int(pwmRegex.match(args).group('RIGHT')))

            elif msgResult.group('CMD') == 'IRVAL':
                if msgResult.group('QUERY'):
                    sendtobase( '[' + ', '.join(map(str, self.info.ir_sensors.readings)) + ']' )

            elif msgResult.group('CMD') == 'ENVAL':
                if msgResult.group('QUERY'):
                    sendtobase( '[{}, {}]'.format(self.info.wheels.left_ticks, self.info.wheels.right_ticks) )

            elif msgResult.group('CMD') == 'ENVEL':
                if msgResult.group('QUERY'):
                    sendtobase( '[{}, {}]'.format(*self.v2pwm(*self.ang_velocity)) )

            elif msgResult.group('CMD') == 'RESET':
                self.info.wheels.left_ticks = 0.0
                self.info.wheels.left_ticks = 0.0
                print('Encoder values reset to [0.0, 0.0]')

            elif msgResult.group('CMD') == 'UPDATE':
                if msgResult.group('SET') and msgResult.group('ARGS'):
                    args = msgResult.group('ARGS')
                    pwmArgPattern = r'(?P<LEFT>[-]?\d+),(?P<RIGHT>[-]?\d+)'
                    pwmRegex = re.compile(pwmArgPattern)
                    pwmResult = pwmRegex.match(args)
                    if pwmResult:
                        self.setPWM(int(pwmRegex.match(args).group('LEFT')), int(pwmRegex.match(args).group('RIGHT')))

                    sendtobase( '[{:.0f}, {:.0f}, {:.0f}, {:.0f}]'.format(self.info.wheels.left_ticks, \
                                                                          self.info.wheels.right_ticks, \
                                                                          *self.v2pwm(*self.ang_velocity))
)

            elif msgResult.group('CMD') == 'END':
                print('Quitting QuickBot run loop')
                raise ValueError('Sorry, cannot stop emulated QuickBot')
                
if __name__ == "__main__":
    # JP limits
    #v = max(min(v,0.314),-0.3148);
    #w = max(min(w,2.276),-2.2763);
    # Real limits
    k = QuickBot(Pose(0,0,0))
    k.set_wheel_speeds(1000,1000)
    print(k.diff2uni(k.get_wheel_speeds()))
    k.set_wheel_speeds(1000,-1000)
    print(k.diff2uni(k.get_wheel_speeds()))
    # 0.341 and 7.7