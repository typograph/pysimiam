#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.week2 import QuickBotSupervisor
from helpers import Struct
from pose import Pose
from numpy import array, dot
from numpy.polynomial.polynomial import polyval
from simobject import Path

from math import pi, sin, cos, log1p, sqrt, atan2

class QuickBotSupervisor2(QuickBotSupervisor):
    """This class solves the Programming Assignment Week2."""

    ir_p = array([6.91029547e-01,  -3.14123891e-03,   7.90448872e-06,
        -1.17852197e-08,   1.02533867e-11,  -4.77674840e-15,
         9.15590826e-19])
    
    ir_p5 = array([  6.30060268e-01,  -2.42595835e-03,   4.75040381e-06,
        -5.01567301e-09,   2.70256281e-12,  -5.81326864e-16])
                                  
    def uni2diff(self,uni):
        """Convert from unicycle model to differential model"""
        (v,w) = uni

        summ = 2*v/self.robot.wheels.radius
        diff = self.robot.wheels.base_length*w/self.robot.wheels.radius

        vl = (summ-diff)/2
        vr = (summ+diff)/2

        return (vl,vr)
            
    def get_ir_distances(self):
        """Converts the IR distance readings into a distance in meters"""
        
        return polyval(self.robot.ir_sensors.readings,self.ir_p)
    

    def estimate_pose(self):
        """Update self.pose_est using odometry"""
        
        # Get tick updates
        dtl = self.robot.wheels.left_ticks - self.prev_left_ticks
        dtr = self.robot.wheels.right_ticks - self.prev_right_ticks
        
        # Save the wheel encoder ticks for the next estimate
        self.prev_left_ticks += dtl
        self.prev_right_ticks += dtr
        
        x, y, theta = self.pose_est

        R = self.robot.wheels.radius
        L = self.robot.wheels.base_length
        m_per_tick = (2*pi*R)/self.robot.wheels.ticks_per_rev
            
        # distance travelled by left wheel
        dl = dtl*m_per_tick
        # distance travelled by right wheel
        dr = dtr*m_per_tick
            
        theta_dt = (dr-dl)/L
        theta_mid = theta + theta_dt/2
        dst = (dr+dl)/2
        x_dt = dst*cos(theta_mid)
        y_dt = dst*sin(theta_mid)
            
        theta_new = theta + theta_dt
        x_new = x + x_dt
        y_new = y + y_dt
           
        #self.log("{} {} {}".format(x_dt,y_dt,theta_dt))
        #self.log("{} - {}, {} - {}".format(self.robot.wheels.left_ticks,
                                           #self.prev_left_ticks, self.robot.wheels.right_ticks,
                                           #self.prev_right_ticks))
           
        return Pose(x_new, y_new, (theta_new + pi)%(2*pi)-pi)
            
    