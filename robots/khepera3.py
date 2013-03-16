import numpy as np
from pose import Pose
from sensor import ProximitySensor
from robot import Robot
from math import ceil, exp, sin, cos, tan, pi
from helpers import Struct

class Khepera3_IRSensor(ProximitySensor):
    """Inherits from the proximity sensor class. Performs calculations specific to the khepera3 for its characterized proximity sensors"""
    def __init__(self,pose,robot):
        # values copied from SimIAm    
        ProximitySensor.__init__(self, pose, robot, (0.02, 0.2, np.radians(20)))

    def distance_to_value(self,dst):
        """Returns the distance calculation from the distance readings of the proximity sensors""" 
        if dst < self.rmin :
            return 3960;
        else:
            return (3960*exp(-30*(dst-self.rmin)));

class Khepera3(Robot):
    """Inherts for the simobject--->robot class for behavior specific to the Khepera3""" 
    def __init__(self, pose, color = 0xFFFFFF):
        Robot.__init__(self, pose, color)
        
        # create shape
        self._p1 = np.array([[-0.031,  0.043, 1],
                             [-0.031, -0.043, 1],
                             [ 0.033, -0.043, 1],
                             [ 0.052, -0.021, 1],
                             [ 0.057,  0    , 1],
                             [ 0.052,  0.021, 1],
                             [ 0.033,  0.043, 1]])
        self._p2 = np.array([[-0.024,  0.064, 1],
                             [ 0.033,  0.064, 1],
                             [ 0.057,  0.043, 1],
                             [ 0.074,  0.010, 1],
                             [ 0.074, -0.010, 1],
                             [ 0.057, -0.043, 1],
                             [ 0.033, -0.064, 1],
                             [-0.025, -0.064, 1],
                             [-0.042, -0.043, 1],
                             [-0.048, -0.010, 1],
                             [-0.048,  0.010, 1],
                             [-0.042,  0.043, 1]])

        # create IR sensors
        self.ir_sensors = []
              
        ir_sensor_poses = [
                           Pose(-0.038,  0.048, np.radians(128)),
                           Pose( 0.019,  0.064, np.radians(75)),
                           Pose( 0.050,  0.050, np.radians(42)),
                           Pose( 0.070,  0.017, np.radians(13)),
                           Pose( 0.070, -0.017, np.radians(-13)),
                           Pose( 0.050, -0.050, np.radians(-42)),
                           Pose( 0.019, -0.064, np.radians(-75)),
                           Pose(-0.038, -0.048, np.radians(-128)),
                           Pose(-0.048,  0.000, np.radians(180))
                           ]                          
                           
        for pose in ir_sensor_poses:
            self.ir_sensors.append(Khepera3_IRSensor(pose,self))
                                
        # initialize motion
        self.ang_velocity = (0.0,0.0)

        self.info = Struct()
        self.info.wheels = Struct()
        # these were the original parameters
        self.info.wheels.radius = 0.021
        self.info.wheels.base_length = 0.0885
        self.info.wheels.ticks_per_rev = 2764.8
        self.info.speed_factor = 6.2953e-6
        self.info.wheels.left_ticks = 0
        self.info.wheels.right_ticks = 0
        
        self.left_revolutions = 0.0
        self.right_revolutions = 0.0
        
        self.info.ir_sensors = Struct()
        self.info.ir_sensors.poses = ir_sensor_poses
        self.info.ir_sensors.readings = None
        self.info.ir_sensors.rmax = 0.2
        self.info.ir_sensors.rmin = 0.02

    def draw(self,r):
        r.set_pose(self.get_pose())
        r.set_pen(0)
        r.set_brush(0xCCCCCC)
        r.draw_polygon(self._p2)
        r.set_pen(0x01000000)
        r.set_brush(self.get_color())
        r.draw_polygon(self._p1)
        
    def get_envelope(self):
        return self._p2
    
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
        
    def get_info(self):
        self.info.ir_sensors.readings = [sensor.reading() for sensor in self.ir_sensors]
        return self.info
    
    def set_inputs(self,inputs):
        self.set_wheel_speeds(inputs)
    
    def diff2uni(self,diff):
        (vl,vr) = diff
        v = (vl+vr) * self.info.wheels.radius/2;
        w = (vr-vl) * self.info.wheels.radius/self.info.wheels.base_length;
        return (v,w)
    
    def get_wheel_speeds(self):
        return self.ang_velocity
    
    def set_wheel_speeds(self,*args):
        if len(args) == 2:
            (vl, vr) = args
        else:
            (vl, vr) = args[0]
            
        # The acceptable wheel velocities are such
        # that 0xFFFF00 / ttick is an integer not greater than 48000
        # If vl and vr are wheel angular velocities
        # this means that ttick = 2*pi / v*ticks_per_rev
        # and a factor depending on controller settings
        # The default is 20e6/8
        
        mult = self.info.wheels.ticks_per_rev * 0xFFFF00 * 8 / 20e6 / 2 / pi
        
        left_ms  = max(-48000, min(48000, int(mult * vl)))
        right_ms = max(-48000, min(48000, int(mult * vr)))

        self.ang_velocity = (left_ms/mult, right_ms/mult)

    def get_external_sensors(self):
        return self.ir_sensors

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        for sensor in self.ir_sensors:
            sensor.draw(renderer)
            
    def update_sensors(self):
        for sensor in self.ir_sensors:
            sensor.update_distance()
    
if __name__ == "__main__":
    # JP limits
    #v = max(min(v,0.314),-0.3148);
    #w = max(min(w,2.276),-2.2763);
    # Real limits
    k = Khepera3(Pose(0,0,0))
    k.set_wheel_speeds(1000,1000)
    print(k.diff2uni(k.get_wheel_speeds()))
    k.set_wheel_speeds(1000,-1000)
    print(k.diff2uni(k.get_wheel_speeds()))
    # 0.341 and 7.7
