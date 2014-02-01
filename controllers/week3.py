#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controller import Controller
import math
import numpy

class GoToGoal(Controller):
    """Go-to-goal steers the robot to a predefined position in the world."""
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
        self.E_k = 0 # Integrated error
        self.e_k_1 = 0 # Previous error calculation
        
        #End Week 3 Assigment

    def get_heading_angle(self, state):
        """Get the heading angle in the world frame of reference."""
        
        #Insert Week 3 Assignment Code Here
        # Here is an example of how to get goal position
        # and robot pose data. Feel free to name them differently.
        
        #x_g, y_g = state.goal.x, state.goal.y
        #x_r, y_r, theta = state.pose
        
        return 0
        #End Week 3 Assigment        

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt.
        state --> the state of the robot and the goal
        dt --> elapsed time
        return --> unicycle model list [velocity, omega]"""
        
        self.heading_angle = self.get_heading_angle(state)
        
        #Insert Week 3 Assignment Code Here
        
        # error between the heading angle and robot's angle
        e_k = 0
        
        # error for the proportional term
        e_P = 0
        
        # error for the integral term. Hint: Approximate the integral using
        # the accumulated error, self.E_k, and the error for
        # this time step, e_k.
        e_I = 0
                    
        # error for the derivative term. Hint: Approximate the derivative
        # using the previous error, obj.e_k_1, and the
        # error for this time step, e_k.
        e_D = 0    
        
        w_ = self.kp*e_P+ self.ki*e_I + self.kd*e_D
        
        v_ = state.velocity.v
        
        # save errors
        self.e_k_1 = e_k
        self.E_k = e_I
        
        #End Week 3 Assignment
        
        return [v_, w_]