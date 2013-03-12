#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class PIDController(Controller):
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

    def get_heading(self, state):
        """Get the direction in which the controller wants to move the robot
        as a vector.
        
        :return: an array [x, y, z] with z = 1.
        """
        raise NotImplementedError("PIDController.get_heading")
    
    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params

        dt --> supervisor set timestep

        return --> unicycle model list [velocity, omega]"""
     
        heading = self.get_heading(state)
        
        v_ = state.velocity.v

        #1. Calculate simple proportional error
        error = math.atan2(heading[1],heading[0])

        #2. Calculate integral error
        self.E += error*dt
        self.E = (self.E + math.pi)%(2*math.pi) - math.pi

        #3. Calculate differential error
        dE = (error - self.error_1)/dt
        self.error_1 = error #updates the error_1 var

        #4. Calculate desired omega
        w_ = self.kp*error + self.ki*self.E + self.kd*dE

        #6. Return solution
        return [v_, w_]
