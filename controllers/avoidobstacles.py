"""
(c) PySimiam Team 2013

Contact person: Tim Fuchs <typograph@elec.ru>

This class was implemented as a weekly programming excercise
of the 'Control of Mobile Robots' course by Magnus Egerstedt.
"""
from pid_controller import PIDController
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

        self.poses = params.sensor_poses

        # Now we know the poses, it makes sense to also
        # calculate the weights
        self.weights = [(math.cos(p.theta)+1.5) for p in self.poses]
        
        # Normalizing weights
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""
        
        # Calculate heading:
        
        # 1. Transform distances to vectors in the robot's frame of reference
        self.vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(state.sensor_distances, self.poses) ] )
        
        # 2. Calculate weighted sum:
        heading = numpy.dot(self.vectors.transpose(), self.weights)
     
        return heading