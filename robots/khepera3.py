import numpy as np
from pose import Pose
from sensor import ProximitySensor
from robot import Robot
from math import ceil, exp, sin, cos, tan, pi
from helpers import Struct

class Khepera3_IRSensor(ProximitySensor):
    def __init__(self,pose,robot):
        # values copied from SimIAm    
        ProximitySensor.__init__(self, pose, robot, (0.02, 0.2, np.radians(20)))

    def distance_to_value(self,dst):
        if dst < self.rmin :
            return 3960;
        else:
            return (3960*exp(-30*(dst-self.rmin)));

class Khepera3(Robot):
    
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
        self.info.wheels.ticks_per_rev = 2765
        self.info.speed_factor = 6.2953e-6
        self.info.wheels.left_ticks = 0
        self.info.wheels.right_ticks = 0
        
        self.info.ir_sensors = Struct()
        self.info.ir_sensors.poses = ir_sensor_poses
        self.info.ir_sensors.readings = None
        
        #self.integrator = ode(motion_f,motion_jac)
        #self.integrator.set_integrator('dopri5',atol=1e-8,rtol=1e-8)

    def draw(self,r):
        r.set_pose(self.get_pose())
        r.set_brush(0xCCCCCC)
        r.draw_polygon(self._p2)
        r.set_brush(self.get_color())
        r.draw_polygon(self._p1)
        
    def get_envelope(self):
        return self._p2
    
    def move(self,dt):

        # There's no need to use the integrator - these equations have a solution        
        (v,w) = self.diff2uni(self.get_wheel_speeds())
        x, y, theta = self.get_pose()
        if w == 0:
            x += v*cos(theta)*dt
            y += v*sin(theta)*dt
        else:
            dtheta = w*dt
            x += v/w*cos(theta + dtheta/2)*sin(dtheta/2)
            y += v/w*sin(theta + dtheta/2)*sin(dtheta/2)
            theta += dtheta
        
        self.set_pose(Pose(x, y, theta))
        
        # FIXME hack for wheel encoders
        ticks_per_m = self.info.wheels.ticks_per_rev/(2*pi*self.info.wheels.radius)
        traveled = v*dt
        dtheta = w*dt
        self.info.wheels.left_ticks += ticks_per_m*(traveled - dtheta*self.info.wheels.base_length/2)
        self.info.wheels.right_ticks += ticks_per_m*(traveled + dtheta*self.info.wheels.base_length/2)
        
    def get_info(self):
        self.info.ir_sensors.readings = [sensor.reading() for sensor in self.ir_sensors]
        return self.info
    
    def set_inputs(self,inputs):
        self.set_wheel_speeds(inputs)
    
    #def __coerce_wheel_speeds(self):
        #(v,w) = self.get_unicycle_speeds();
        #v = max(min(v,0.3148),-0.3148);
        #w = max(min(w,2.2763),-2.2763);
        #self.ang_velocity = self.uni2diff((v,w))
    
    def diff2uni(self,diff):
        (vl,vr) = diff
        v = self.info.wheels.radius/2*(vl+vr);
        w = self.info.wheels.radius/self.info.wheels.base_length*(vr-vl);
        return (v,w)

    #def uni2diff(self,uni):
        #(v,w) = uni
        ## Assignment Week 2
        #vr = (self.info.wheels.base_length*w +2*v)/2/self.info.wheels.radius
        #vl = vr - self.info.wheels.base_length*w/self.info.wheels.radius
        ## End Assignment
        #return (vl,vr)
    
    def get_wheel_speeds(self):
        return self.ang_velocity
    
    def set_wheel_speeds(self,*args):
        if len(args) == 2:
            self.ang_velocity = args
        else:
            self.ang_velocity = args[0]
        #self.__coerce_wheel_speeds()

    #def set_unicycle_speeds(self,*args):
        #if len(args) == 2:
            #self.ang_velocity = self.uni2diff(args)
        #else:
            #self.ang_velocity = self.uni2diff(args[0])
        #self.__coerce_wheel_speeds()

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
    k = Khepera3(Pose(0,0,0))
    print(k.diff2uni(k.uni2diff((1,2))))
    print(k.uni2diff(k.diff2uni((1,2))))
    print(k.diff2uni((100,80)))
