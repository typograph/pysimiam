"""
(c) PySimiam Team 2013 

Contact person: Tim Fuchs <typograph@elec.ru>

This class was implemented as a weekly programming excercise
of the 'Control of Mobile Robots' course by Magnus Egerstedt.
"""
from pid_controller import PIDController
import math
import numpy

class GoToGoal(PIDController):
    """Go-to-goal steers the robot to a predefined position in the world."""
    def __init__(self, params):
        """Initialize internal variables"""
        PIDController.__init__(self,params)

    def get_heading(self, state):
        """Get the direction from the robot to the goal as a vector."""
        
        # The goal:
        x_g, y_g = state.goal.x, state.goal.y
        
        # The robot:
        x_r, y_r, theta = state.pose

        # Where is the goal in the robot's frame of reference?
        goal_angle = math.atan2(y_g - y_r, x_g - x_r) - theta
        
        # Alternative implementation:
        # return numpy.dot(
        #     numpy.linalg.pinv(state.pose.get_transformation()),
        #     numpy.array([state.goal.x, state.goal.y, 1]))
        
        return numpy.array([math.cos(goal_angle),math.sin(goal_angle),1])        
