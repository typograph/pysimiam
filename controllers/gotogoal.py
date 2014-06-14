#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

import math
import numpy

from controllers.pid_controller import PIDController

class GoToGoal(PIDController):
    """Go-to-goal steers the robot to a predefined position in the world.
    
       The state of this controller expected in execute
       should be the pose of the robot (:class:`~pose.Pose`).
    """
    def __init__(self):
        """Initialize internal variables"""
        PIDController.__init__(self)

    def set_parameters(self, ks, v, goal):
        """Set the parameters of this controller
        
        :param ks: PID gains
        :type  ks: (kp, ki, kd)
        :param v: Target speed
        :type  v: float
        :param goal: The goal to be reached
        :type  goal: A structure containing x and y fields
        """
        kp, ki, kd = ks
        PIDController.set_parameters(self, kp, ki, kd, v)
        self.goal = goal        

    # Let's overwrite this way:
    def get_heading_angle(self, state):
        """Get the direction from the robot to the goal as a vector."""
        
        # The goal:
        x_g, y_g = self.goal.x, self.goal.y
        
        # The robot:
        x_r, y_r, theta = state

        # Where is the goal in the robot's frame of reference?
        return (math.atan2(y_g - y_r, x_g - x_r) - theta + math.pi)%(2*math.pi) - math.pi

    def get_heading(self, state):

        goal_angle = self.get_heading_angle(state)
        return numpy.array([math.cos(goal_angle),math.sin(goal_angle),1])
