#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from pid_controller import PIDController
import math
import numpy

class GoToGoal(PIDController):
    """Example of PID implementation for goal-seek"""
    def __init__(self, params):
        """init
        @params: 

        """
        PIDController.__init__(self,params)
        self.goal_angle = 0

    def get_heading(self, state):
        #Calculate the goal position
        x_g, y_g = state.goal.x, state.goal.y
        x_r, y_r, theta = state.pose

        self.goal_angle = math.atan2(y_g - y_r, x_g - x_r) - theta
        
        return numpy.array([math.cos(self.goal_angle),math.sin(self.goal_angle),1])        
