#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.pid_controller import PIDController
import math
import numpy

class GoToGoal(PIDController):
    """Go-to-goal steers the robot to a predefined position in the world."""
    def __init__(self, params):
        """Initialize internal variables"""
        PIDController.__init__(self,params)

    # Let's overwrite this way:
    def get_heading_angle(self, state):
        """Get the direction from the robot to the goal as a vector."""
        
        # The goal:
        x_g, y_g = state.goal.x, state.goal.y
        
        # The robot:
        x_r, y_r, theta = state.pose

        # Where is the goal in the robot's frame of reference?
        return (math.atan2(y_g - y_r, x_g - x_r) - theta + math.pi)%(2*math.pi) - math.pi

    def get_heading(self,state):

        goal_angle = self.get_heading_angle(state)
        return numpy.array([math.cos(goal_angle),math.sin(goal_angle),1])
    
    def execute(self, state, dt):
        
        v, w = PIDController.execute(self, state, dt)
        
        # Week 5 code
        #
        # 
        
        return v, w