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

        self.away_angle = 0
        self.vectors = []

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.poses = params.sensor_poses
        self.weights = [1.0]*len(self.poses)
        #self.weights = [(math.cos(p.theta)+1.5) for p in self.poses]
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""      
        
        # Calculate vectors:
        self.vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(state.sensor_distances, self.poses) ] )
        
        # Calculate weighted sum:
        heading = numpy.dot(self.vectors.transpose(), self.weights)
     
        self.away_angle = math.atan2(heading[1],heading[0])
        
        return heading