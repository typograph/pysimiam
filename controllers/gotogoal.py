"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: Example PID implementation for goal-seek (incomplete)
"""
from controller import Controller
import math
import numpy

class GoToGoal(Controller):
    def __init__(self, params):
        Controller.__init__(self,params)

        self.E_k = 0 # integrated error
        self.e_k_1 = 0 # last step error

    def set_parameters(self,params):
        self.kp = params.kp
        self.ki = params.ki
        self.kd = params.kd

    def execute(self,state,dt):

        x_g, y_g = state.goal.x, state.goal.y
        x_r, y_r, theta = state.pose

        e_k = math.atan2(y_g - y_r, x_g - x_r) - theta
        e_k = math.atan2(math.sin(e_k), math.cos(e_k))

        self.E_k += e_k*dt
        
        _w = self.kp*e_k + \
             self.ki*self.E_k + \
             self.kd*(e_k - self.e_k_1)/dt

        self.e_k_1 = e_k
        
        return [state.velocity, _w]
