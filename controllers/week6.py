#PySimiam
#Author: Tim Fuchs
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from pid_controller import PIDController
import math
import numpy

class FollowWall(PIDController):
    """Follow walls is an example controller that keeps a certain distance
    to the wall and drives alongside it in clockwise or counter-clockwise
    fashion."""
    def __init__(self, params):
        ''' It's just a PID controller'''
        PIDController.__init__(self,params)

        self.vectors = []
        
    def restart(self):
        PIDController.restart(self)

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.poses = params.sensor_poses
        self.direction = params.direction
        self.distance = params.distance

    def get_heading(self, state):
        """Get the direction along the wall as a vector."""
        
        # Week 6 Assignment:
        
        # Calculate vectors for the sensors
        self.vectors = []

        # Calculate the two vectors:
        self.to_wall_vector = [0,0.3,1]
        self.along_wall_vector = [0.3,0,1]
                            
        # Calculate and return the heading vector:                            
        return self.along_wall_vector
    
        # End Week 6 Assignment
               