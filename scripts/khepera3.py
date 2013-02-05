import numpy as np
from pose import Pose
from sensor import IRSensor
from robot import Robot
from math import ceil,exp,sin,cos
from scipy.integrate import ode

class Khepera3_IRSensor(IRSensor):
    def __init__(self,pose,robot):
        super(Khepera3_IRSensor, self).__init__(pose,robot)
        # values copied from SimIAm
        self.rmin = 0.02
        self.rmax = 0.2
        self.phi  = np.radians(20)
    
    @classmethod
    def __distance_to_value(dst):
        if dst < self.rmin :
            return 3960;
        else:
            return (3960*exp(-30*(dst-self.rmin)));
   
    def reading(self):
        pass

def motion_f(t,y):
    """The Drive problem
    """
    theta,v,w = y[2:]
    return (v*cos(theta),-v*sin(theta),w,0,0)

def motion_jac(t,y):
    """The Jacobian of the drive problem
    """
    (x,y,theta,v,w) = y
    
    j = np.zeros((5,5))
    j[1][3] = -v*sin(theta) # d(v*cos(theta))/dtheta
    j[2][3] = -v*cos(theta) # d(v*cos(theta))/dtheta
    j[1][4] = cos(theta) # d(v*cos(theta))/dv
    j[2][4] = -sin(theta) # d(-v*sin(theta))/dv
    j[3][5] = 1 # dw/dw
    return (v*cos(theta),-v*sin(theta),w,0,0)

class Khepera3(Robot):
    
    def __init__(self, pose):
        #super(Khepera3, self).__init__(pose)
        
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

        self.wheel_radius = 21.0
        self.wheel_base_length = 88.5
#       #I'm not sure we need those
#        self.ticks_per_rev = 2765
#        self.speed_factor = 6.2953e-6

        self.integrator = ode(motion_f,motion_jac)
        self.integrator.set_integrator('dopri5',atol=1e-8,rtol=1e-8)

    def draw(self,gc):
        gc.PushState()
        gc.SetTransform(self.getPose().getGraphicsMatrix(gc))
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour('GREY'))))
        gc.DrawLines(self._p2)
        gc.SetBrush(gc.CreateBrush(wx.Brush(wx.Colour('BLUE'))))
        gc.DrawLines(self._p1)
        gc.PopState()               
        
    def getEnvelope(self):
        return self._p2
        
    def PoseAfter(self,dt):
#        print('(vel_r,vel_l) = (%0.6g,%0.6g)\n' % self.ang_velocity);
#        print('Calculated velocities (v,w): (%0.3g,%0.3g)\n' % self.getUniformSpeeds());
        self.integrator.set_initial_value(self.Pose().getPoseList() + list(self.getUniformSpeeds()),0)
        self.integrator.integrate(dt)
        return Pose(r.y[:3]);
    
    def __coerce_wheel_speeds(self):
        (v,w) = self.getUniformSpeeds();
        v = max(min(v,0.314),-0.3148);
        w = max(min(w,2.276),-2.2763);
        self.ang_velocity = self.uni2diff((v,w))
    
    def diff2uni(self,diff):
        (vl,vr) = diff
        v = self.wheel_radius/2*(vl+vr);
        w = self.wheel_radius/self.wheel_base_length*(vr-vl);
        return (v,w)

    def uni2diff(self,uni):
        (v,w) = uni
        # Assignment Week 2
        vl = 0.0
        wl = 0.0
        # End Assignment
        return (vl,vr)
    
    def getDifferentialSpeeds(self):
        return self.ang_velocity
    
    def getUniformSpeeds(self):
        return self.diff2uni(self.getDifferentialSpeeds())
    
    def setWheelSpeeds(self,*args):
        if len(args) == 2:
            self.ang_velocity = args
        else:
            self.ang_velocity = args
        self.___coerce_wheel_speeds()
