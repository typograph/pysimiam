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

class FollowWall(PIDController):
    """Follow walls is a controller that keeps a certain distance
    to the wall and drives alongside it in clockwise or counter-clockwise
    fashion."""
    def __init__(self, params):
        '''Initialize internal variables'''
        PIDController.__init__(self,params)

        # This variable should contain a list of vectors
        # calculated from the relevant sensor readings.
        # It is used by the supervisor to draw & debug
        # the controller's behaviour
        self.vectors = []
        
    def restart(self):
        """Reset internal state"""
        PIDController.restart(self)

    def set_parameters(self, params):
        """Set PID values, sensor poses, direction and distance.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``, the direction of wall
        following (either 'right' for clockwise or 'left' for anticlockwise)
        as ``params.direction`` and the desired distance to the wall 
        to maintain as ``params.distance``.
        """
        PIDController.set_parameters(self,params)

        self.sensor_poses = params.sensor_poses
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
               