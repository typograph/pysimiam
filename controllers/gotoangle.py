#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
import math

from core.controller import Controller

class GoToAngle(Controller):
    """Go-to-goal steers the robot to a predefined position in the world.
    
       The state of this controller expected in execute
       should be the pose of the robot (:class:`~pose.Pose`).
    """
    def __init__(self):
        """Initialize internal variables"""
        Controller.__init__(self)

    def set_parameters(self, kp, v, goal_angle):
        """Set PID values
        
        :param kp: Proportional gain
        :type kp: float
        :param v: Target speed
        :type v: float
        :param goal_angle: Target direction
        :type goal_angle: float
        """
        self.kp = kp
        self.v = v
        self.goal = goal_angle
               
    def execute(self, state, dt):
        """Calculate errors and steer the robot
        
        :param state: The estimated robot pose
        :type state: :class:`~pose.Pose`
        :param dt: time since last call
        :type dt: float
        
        """
     
        # The goal:
        theta_g = self.goal*math.pi/180
        
        # The robot:
        x_r, y_r, theta = state

        # 1. Calculate simple proportional error
        error = (theta_g - theta + math.pi)%(2*math.pi) - math.pi

        # 2. Calculate desired omega
        w_ = self.kp*error
        
        # 3. The linear velocity is given to us:
        return [self.v, w_]
