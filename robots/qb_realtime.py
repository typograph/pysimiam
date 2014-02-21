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
from robot import RealBot
from math import ceil, exp, sin, cos, tan, pi
from helpers import Struct
from simobject import Cloud
from .qb_realtime_comm import qb_comm, socket

def sign(x):
    if x == 0:
        return 0
    if x > 0:
        return 1
    return -1

class QuickBot(RealBot, qb_comm):
    """Communication with a QuickBot""" 
    
    ir_coeff = np.array([ 8.56495710e-18,  -3.02930608e-14,
                          4.43025017e-11,  -3.49052288e-08,
                          1.61452174e-05,  -4.44025236e-03,
                          6.74137385e-1])
    beta = (1.0, 0.0)

    def __init__(self, pose, color = 0xFFFFFF, options = None):
       
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
        
        ir_sensor_poses = [
                          Pose(-0.0474, 0.0534, np.radians(90)),
                          Pose( 0.0613, 0.0244, np.radians(45)),
                          Pose( 0.0636, 0.0, np.radians(0)),
                          Pose( 0.0461,-0.0396, np.radians(-45)),
                          Pose(-0.0690,-0.0534, np.radians(-90))
                          ]                          
        
        self.info = Struct()
        self.info.wheels = Struct()

        self.info.wheels.radius = 0.0325
        self.info.wheels.base_length = 0.09925
        self.info.wheels.ticks_per_rev = 16
        self.info.wheels.left_ticks = 0
        self.info.wheels.right_ticks = 0
        
        self.info.wheels.max_velocity = 2*pi*130/60 # 130 RPM
        self.info.wheels.min_velocity = 2*pi*30/60  #  30 RPM

        self.info.wheels.vel_left = 0
        self.info.wheels.vel_right = 0

        self.info.ir_sensors = Struct()
        self.info.ir_sensors.poses = ir_sensor_poses
        self.info.ir_sensors.rmax = 0.3
        self.info.ir_sensors.rmin = 0.04
        self.info.ir_sensors.readings = [133]*len(self.info.ir_sensors.poses)

        self.walls = Cloud(0) # Black, no readings

        # The constructor is called here because otherwise set_pose fails
        RealBot.__init__(self, pose, color)
        
        # Connect to bot...
        # This code will raise an exception if not able to connect
        
        if options is None:
            self.log("No IP/port supplied to connect to the robot")
            qb_comm.__init__(self, "localhost", "localhost", 5005)
        else:
            try:
                qb_comm.__init__(self, options.baseIP, options.robotIP, options.port)
            except AttributeError:
                self.log("No IP/port supplied in the options to connect to the robot")
                qb_comm.__init__(self, "localhost", "localhost", 5005)
                
        self.ping() # Check if the robot is there

        self.pause() # Initialize self.__paused
                
    def set_pose(self,rpose):
        RealBot.set_pose(self,rpose)
        
        # We have to update walls here. WHY?
        for pose, dst in zip(self.info.ir_sensors.poses,np.polyval(self.ir_coeff, self.info.ir_sensors.readings)):
            if dst/self.info.ir_sensors.rmax <= 0.99:
                self.walls.add_point(Pose(dst) >> pose >> self.get_pose())

    def draw(self,r):
        self.walls.draw(r)
        
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
           
    def draw_sensor(self,renderer,pose,dst):
        
        renderer.push_state()
        renderer.add_pose(pose)
        
        phi = np.radians(3) # 6/2
        rmin = self.info.ir_sensors.rmin
        rmax = self.info.ir_sensors.rmax

        if dst/rmax > 0.99:
            renderer.set_brush(0x33FF5566)
        else:
            renderer.set_brush(0xCCFF5566)

        renderer.draw_ellipse(0,0,min(1,rmin/2),min(1,rmin/2))
        
        renderer.draw_polygon([(rmin*cos(phi),rmin*sin(phi)),
                       (dst*cos(phi),dst*sin(phi)),
                       (dst,0),
                       (dst*cos(phi),-dst*sin(phi)),
                       (rmin*cos(phi),-rmin*sin(phi))])
        
        renderer.pop_state()
    
    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        renderer.set_pose(self.get_pose())
        
        distances = np.polyval(self.ir_coeff,self.info.ir_sensors.readings)
        for pose, distance in zip(self.info.ir_sensors.poses, distances):
            self.draw_sensor(renderer,pose,distance)

    def get_info(self):
        return self.info
    
    def v2pwm(self,vl,vr):
        """Convert from angular velocity to PWM"""

        pwm_l = sign(vl)*(abs(vl) - self.beta[1])/self.beta[0];
        pwm_r = sign(vr)*(abs(vr) - self.beta[1])/self.beta[0];        

        return pwm_l, pwm_r

    def pwm2v(self,pwm_l,pwm_r):
        """Convert from PWM to angular velocity"""
        vl = sign(pwm_l)*(self.beta[0]*abs(pwm_l) + self.beta[1])
        vr = sign(pwm_r)*(self.beta[0]*abs(pwm_r) + self.beta[1])

        return vl, vr        

    def set_inputs(self,inputs):
        pwm_l, pwm_r = self.v2pwm(*inputs)
       
        with self.connect() as connection:
            self.set_pwm(pwm_l, pwm_r, connection)
            speeds = self.get_pwm(connection)
            if speeds is None:
                raise RuntimeError("Communication with QuickBot failed")
        
        if speeds is not None:
            self.info.wheels.vel_left, self.info.wheels.vel_right = self.pwm2v(*speeds)

    def update_external_info(self):
        "Communicate with the robot"
        
        if self.__paused:
            return
        
        with self.connect() as connection:
            ticks = self.get_encoder_ticks(connection)
            if ticks is None:
                raise RuntimeError("Communication with QuickBot failed")
            
            self.info.wheels.left_ticks, self.info.wheels.right_ticks = ticks

            irs = self.get_ir_raw_values(connection)
            if irs is None:
                raise RuntimeError("Communication with QuickBot failed")
            
            self.info.ir_sensors.readings = irs

    def reset(self):        
        self.__paused = True
        self.info.wheels.vel_left, self.info.wheels.vel_right = 0,0
        self.send_reset()
        
    def pause(self):        
        self.__paused = True
        self.send_halt()
    
    def resume(self):
        self.__paused = False
        self.set_inputs((self.info.wheels.vel_left, self.info.wheels.vel_right))

