#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

import math
import numpy

from controllers.gotogoal import GoToGoal
from controllers.avoidobstacles import AvoidObstacles

class Blending(GoToGoal, AvoidObstacles):
    """A controller blending go-to-goal and avoid-obstacles behaviour"""
    def __init__(self, sensor_poses, sensor_weights):
        """Initialize internal variables"""
        GoToGoal.__init__(self)
        AvoidObstacles.__init__(self, sensor_poses, sensor_weights)

        # These two angles are used by the supervisor
        # to debug the controller's behaviour, and contain
        # the headings as returned by the two subcontrollers.
        self.goal_angle = 0
        self.away_angle = 0
        
    def get_ao_heading(self,sensor_distances):
        """Get the direction away from the obstacles as a vector."""
        return AvoidObstacles.get_heading(self, sensor_distances)        

    def get_gtg_heading(self, robot_pose):
        """Get the direction from the robot to the goal as a vector."""        
        return GoToGoal.get_heading(self, robot_pose)

    def get_heading(self, state):
        """Blend the two headings
        
           The state should have two fields:
           state.sensor_distances: The list of sensor-obstacle distances
           state.pose: The pose of the robot
        """
        
        # Get the outputs of the two subcontrollers
        u_ao = self.get_ao_heading(state.sensor_distances)
        self.away_angle = math.atan2(u_ao[1],u_ao[0])
        
        u_gtg = self.get_gtg_heading(state.pose)
        self.goal_angle = math.atan2(u_gtg[1],u_gtg[0])
        
        # The closer we are to the obstacles, the less weight go-to-goal has
        weight_gtg = math.exp(- 0.2 / min(state.sensor_distances) + 1)
        
        u = u_ao*(1-weight_gtg) + u_gtg*weight_gtg
                
        return u
