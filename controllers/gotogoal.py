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
        #Week 3
        #Place any variables you would like to store here
        #You may use this variables for convenience
        self.E = 0 # Integrated error
        self.e_1 = 0 # Previous error calculation

        #End week3

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
        #Week 3
        # Here is an example of how to get goal position
        # and robot pose data. Feel free to name them differently.

        #x_g, y_g = state.goal.x, state.goal.y
        #x_r, y_r, theta = state.pose

        #Your goal is to modify these two variables
        w_ = 0
        v_ = 0 

        #End week3 exercise
        return [v_, w_]
