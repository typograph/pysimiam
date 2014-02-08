#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.week4 import AvoidObstacles as AvoidObstaclesStub
import math
import numpy
from pose import Pose

class AvoidObstacles(AvoidObstaclesStub):
    """Avoid obstacles is an example controller that checks the sensors
       for any readings, constructs 'obstacle' vectors and directs the robot
       in the direction of their weightd sum."""

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        AvoidObstaclesStub.set_parameters(self,params)

        # Now we know the poses, it makes sense to also
        # calculate the weights
        self.weights = [(math.cos(p.theta/2)+0.5) for p in self.sensor_poses]
        
        # Normalizing weights
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""
        
        # Week 4 Assignment:
        
        # Calculate vectors: (that's only for drawing, actual code can be simpler)
        self.vectors = [ list(Pose(d) >> p) \
                            for d, p in zip(state.sensor_distances, self.sensor_poses) ]
        
        # Calculate weighted sum:
        x, y = 0, 0
        for v,w in zip(self.vectors, self.weights):
            x += v[0]*w
            y += v[1]*w
                
        # End Week 4 Assignment
     
        return x, y, 1