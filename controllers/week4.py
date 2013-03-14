#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from pid_controller import PIDController
import math
import numpy

class AvoidObstacles(PIDController):
    """Avoid obstacles is an example controller that checks the sensors for any readings, checks a threshold, and then performs counter-clockwise evasion from the first detected sensor position. Speed control and goal selection are a part of its routines."""
    def __init__(self, params):
        '''read another .xml for PID parameters?'''
        PIDController.__init__(self,params)

        self.vectors = []

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.poses = params.sensor_poses
        
        # Week 4 assigment
        # Set the weigths here
        self.weights = [1]*len(self.poses)

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""      
        
        # Week 4 Assignment:
        
        # Calculate vectors:
        self.vectors = []
        
        # Calculate weighted sum:
        heading = [1, 0, 1]
     
        # End Week 4 Assignment
     
        return heading