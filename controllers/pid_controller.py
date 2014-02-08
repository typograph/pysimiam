#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controller import Controller
import math
import numpy

class PIDController(Controller):
    """The PID controller is a general-purpose controller that steers the robot to a certain heading direction. The heading is recalculated on every execution."""
    def __init__(self, params):
        '''Initialize internal variables'''
        Controller.__init__(self,params)
        
        # This angle shows the direction that the controller
        # tries to follow. It is used by the supervisor
        # to draw and debug this controller
        self.heading_angle = 0

    def restart(self):
        """Set the integral and differential errors to zero"""
        self.E = 0
        self.error_1 = 0

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

    def get_heading(self, state):
        """Get the direction in which the controller wants to move the robot
        as a vector in the robot's frame of reference.
        
        :return: a numpy array [x, y, z] with z = 1.
        """
        raise NotImplementedError("PIDController.get_heading")
    
    def get_heading_angle(self, state):
        """Return the heading as an angle in the robot's frame of reference."""

        # The vector to follow
        heading = self.get_heading(state)

        return math.atan2(heading[1],heading[0])
    
    def execute(self, state, dt):
        """Calculate errors and steer the robot"""
     
        # This is the direction we want to go
        self.heading_angle = self.get_heading_angle(state)

        # 1. Calculate simple proportional error
        # The direction is in the robot's frame of reference,
        # so the error is the direction.
        # Note that the error is automatically between pi and -pi.
        error = self.heading_angle

        # 2. Calculate integral error
        self.E += error*dt
        self.E = (self.E + math.pi)%(2*math.pi) - math.pi

        # 3. Calculate differential error
        dE = (error - self.error_1)/dt
        self.error_1 = error #updates the error_1 var

        # 4. Calculate desired omega
        w_ = self.kp*error + self.ki*self.E + self.kd*dE
        
        # The linear velocity is given to us:
        v_ = state.velocity.v

        return [v_, w_]
