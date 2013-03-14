#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class GoToGoal(Controller):
    """Example of a PID implementation for goal-seek"""
    def __init__(self, params):
        '''Initialize some variables'''
        
        Controller.__init__(self,params)
        self.heading_angle = 0

    def set_parameters(self, params):
        """Set PID values
        
        The params structure is expected to have in the `gains` field three
        parameters for the PID gains.
        
        :param params.gains.kp: Proportional gain
        :type params.gains.kp: float
        :param params.gains.ki: Integral gain
        :type params.gains.ki: float
        :param params.gains.kd: Differential gain
        :type params.gains.kd: float
        """
        self.kp = params.gains.kp
        self.ki = params.gains.ki
        self.kd = params.gains.kd

    def restart(self):
        #Week 3 Assignment Code:
        #Place any variables you would like to store here
        #You may use these variables for convenience
        self.E = 0 # Integrated error
        self.e_1 = 0 # Previous error calculation

        #End Week 3 Assigment

    def get_heading(self, state):
        """Get the vector pointing in the right direction in the form [x, y, 1]."""
        
        #Insert Week 3 Assignment Code Here
        # Here is an example of how to get goal position
        # and robot pose data. Feel free to name them differently.

        #x_g, y_g = state.goal.x, state.goal.y
        #x_r, y_r, theta = state.pose

        #End Week 3 Assigment
        
        return [1, 0, 1]
    
    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params
        dt --> supervisor set timestep
        return --> unicycle model list [velocity, omega]"""
     
        heading = self.get_heading(state)      
        self.heading_angle = math.atan2(heading[1],heading[0])

        #Insert Week 3 Assignment Code Here

        w_ = 0
        v_ = 0

        #End Week 3 Assignment
        
        return [v_, w_]