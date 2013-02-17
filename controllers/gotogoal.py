#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class GoToGoal(Controller):
    """Example of PID implementation for goal-seek"""
    def __init__(self, params):
        """init
        @params: 

        """
        Controller.__init__(self,params)

        self.E_k = 0 # integrated error
        self.e_k_1 = 0 # last step error

    def set_parameters(self,params):
        """Set the PID Values
        @params: (float) kp, ki, kd
        """
        self.kp = params.kp
        self.ki = params.ki
        self.kd = params.kd

    def execute(self,state,dt):
        """Executes the controller behavior
        @return --> unicycle model list [velocity, omega]
        """
        #Calculate the goal position
        x_g, y_g = state.goal.x, state.goal.y
        x_r, y_r, theta = state.pose

        #Estimate the error in theta, use atan2
        e_k = math.atan2(y_g - y_r, x_g - x_r) - theta
        e_k = math.atan2(math.sin(e_k), math.cos(e_k))

        #Integral error estimation
        self.E_k += e_k*dt
        
        #Estimate first wheel speed
        _w = self.kp*e_k + \
             self.ki*self.E_k + \
             self.kd*(e_k - self.e_k_1)/dt

        #store error
        self.e_k_1 = e_k
        
        return [state.velocity.v, _w]
