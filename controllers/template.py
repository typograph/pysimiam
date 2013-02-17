from controller import Controller
import math
import numpy

class Template(Controller):
    """Template controller with required functions"""
    def __init__(self, params):
        #Must declare some k values
        self.kp=10
        self.ki=0
        self.kd=0

        #Good idea to initialize some error variables 
        # E - integral error
        # error_1 - the previous error measurement
        self.E = 0
        self.error_1 = 0

    def set_parameters(self, params):
        """Set PID values
        @param: (float) kp, ki, kd
        """
        self.kp = params.kp
        self.ki = params.ki
        self.kd = params.kd

    def execute(self, state, dt):
        """Required function: must return a unicycle model

        return --> unicycle model list [velocity, omega]"""

        #1. Calculate simple proportional error
        #2. Correct for angles (angle may be greater than PI)
        #3. Calculate integral error
        #4. Calculate differential error
        #5. Calculate desired omega

        #You need to modify these values!!
        v_ = 0 #some default value
        w_ = 0 #another default value
        #6. Return solution
        return [v_, w_]
