"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: Example PID implementation for goal-seek (incomplete)
"""
from controller import Controller
import math
import numpy

class Gotogoal(Controller):
    def __init__(self):
        '''read another .xml for PID parameters?'''
        self.kp=10
        self.ki=0
        self.kd=0

        self.E_k = 0
        self.e_k_1 = 0


    def algorithm(self,pose_est,dt):
        #Modify Below Here
        _theta=pose_est().theta
        _destination=[pose_est().x,pose_est().y]

        '''I just define the goal arbitrarily here'''
        _goal=[500,500]
        
        '''I just define the speed arbitrarily here'''
        _v=1
        
        e_k=math.atan2(_destination[1],_destination[0])
        e_k=math.atan2(math.sin(e_k),math.cos(e_k))
        
        _w = self.kp*e_k + self.ki*(self.E_k+e_k*dt) + self.kd*(e_k-self.e_k_1)/dt;

        self.E_k = self.E_k+e_k*dt;
        self.e_k_1 = e_k;
        
        #Modify Above Here
        return [_w,_v]
