"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: Example PID implementation for goal-seek (incomplete)
"""
from controller import Controller
import math
import numpy

class AvoidObstacles(Controller):
    def __init__(self):
        '''read another .xml for PID parameters?'''
        self.kp=10
        self.ki=0
        self.kd=0

        self.E_k = 0
        self.e_k_1 = 0


    def execute(self,pose_est,dt):
        #Modify Below Here
        _theta=pose_est().theta
        _destination=[pose_est().x,pose_est().y]

        #Don't care about a goal bc we care about avoiding object

        
        #Modify Above Here
        return [_w,_v]
