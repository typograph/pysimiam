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

    def set_parameters(self, params):
        """Set PID values
        @param: (float) kp, ki, kd
        """
        self.kp = params.kp
        self.ki = params.ki
        self.kd = params.kd

    def execute(self, state, dt):
        #Select a goal, ccw obstacle avoidance
        #Get distances from sensors 
        distances = state. 
        return [_w,_v]
