#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from pid_controller import PIDController
import math
import numpy

class GoToGoal(PIDController):
    """Example of a PID implementation for goal-seek"""
    def __init__(self, params):
        """Create the go-to-goal controlles.
        
        See :meth:`controller.PIDController.set_params`
        for the expected parameter structure
        """
        PIDController.__init__(self,params)

    def get_heading(self, state):
        """Get the direction from the robot to the goal as a vector."""
        #Calculate the goal position
        x_g, y_g = state.goal.x, state.goal.y
        x_r, y_r, theta = state.pose

        goal_angle = math.atan2(y_g - y_r, x_g - x_r) - theta
        # Alternative implementation:
        # return numpy.dot(
        #     numpy.linalg.pinv(state.pose.get_transformation()),
        #     numpy.array([state.goal.x, state.goal.y, 1]))
        
        return numpy.array([math.cos(goal_angle),math.sin(goal_angle),1])        
