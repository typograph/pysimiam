#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.pid_controller import PIDController
import math
import numpy

class AvoidObstacles(PIDController):
    """Avoid obstacles is an example controller that checks the sensors
       for any readings, constructs 'obstacle' vectors and directs the robot
       in the direction of their weightd sum."""
    def __init__(self, params):
        '''Initialize internal variables'''
        PIDController.__init__(self,params)
        
        # This variable should contain a list of vectors
        # calculated from sensor readings. It is used by
        # the supervisor to draw & debug the controller's
        # behaviour
        self.vectors = []

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.sensor_poses = params.sensor_poses
        
        # Week 4 assigment
        # Set the weigths here
        self.weights = [1]*len(self.sensor_poses)

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""
        
        # Week 4 Assignment:
        
        # Calculate vectors:
        self.vectors = [[0,0,1]]*5
        
        # Calculate weighted sum:
        heading = [1, 0, 1]
     
        # End Week 4 Assignment
     
        return heading