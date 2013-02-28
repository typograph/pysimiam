#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class AvoidObstacles(Controller):
    """Avoid obstacles is an example controller that checks the sensors for any readings, checks a threshold, and then performs counter-clockwise evasion from the first detected sensor position. Speed control and goal selection are a part of its routines."""
    def __init__(self, params):
        '''read another .xml for PID parameters?'''
        Controller.__init__(self,params)
        self.clear_error()

    def clear_error(self):
        self.E = 0
        self.error_1 = 0

    def set_parameters(self, params):
        """Set PID values
        @param: (float) kp, ki, kd
        """
        self.kp = params.gains.kp
        self.ki = params.gains.ki
        self.kd = params.gains.kd

        # Week 4 code 
        # These variables will be used to make calculations
        self.angles = params.sensor_angles
        self.weights = [(math.cos(a)+1.1) for a in self.angles]
        # End week 4 code

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params
        dt --> supervisor set timestep
        return --> unicycle model list [velocity, omega]"""

        #Begin week 4 code

        #1. Store the state values for the robot
        self.robotx, self.roboty, self.robottheta = state.pose

        #2. Make calculations for a new goal 
        #3. Calculate proportional error
        #4. Correct for angles (angle may be greater than PI) with atan2
        #5. Calculate integral error
        #6. Calculate differential error
        # store error in self.e_1

        #7. Calculate desired omega
        #Make sure you modify these variables

        v_ = 0
        w_ = 0 
        
        #End week 4 code
        #8. Return solution
        return [v_, w_]
