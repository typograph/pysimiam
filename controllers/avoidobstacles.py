#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

import math
import numpy

from core.pose import Pose

from controllers.pid_controller import PIDController

class AvoidObstacles(PIDController):
    """Avoid obstacles is an example controller that checks the sensors
    for any readings, constructs 'obstacle' vectors and directs the robot
    in the direction of their weighted sum.
       
    The constructor expects two parameters:
    
    :param sensor_poses: A list of poses of all the sensors in the robot's
                         frame of reference
    :type  sensor_poses: [:class:`~pose.Pose`]
    :param sensor_weights: A list of sensor weights of the same length
                           as *sensor_poses*
    :type  sensor_weights: [float] or None

    The parameters for the :meth:`~controller.Controller.set_parameters`
    are the same as for the :class:`~pid_controller.PIDController`'s
    :meth:`~pid_controller.PIDController.set_parameters`
 
    """
    def __init__(self, sensor_poses, sensor_weights=None):
        '''Initialize internal variables'''
        PIDController.__init__(self)

        self.sensor_poses = sensor_poses

        # Normalizing weights
        if sensor_weights is None:
            sensor_weights = [1]*len(sensor_poses)
        ws = sum(sensor_weights)
        self.weights = [w/ws for w in sensor_weights]

    def get_heading(self, sensor_distances):
        """Get the direction away from the obstacles as a vector."""
        
        # Calculate heading:
        x, y = 0, 0
        for d,p,w in zip(sensor_distances, self.sensor_poses, self.weights):
            pose = Pose(d) >> p
            x += pose.x*w
            y += pose.y*w
                
        return numpy.array([x, y, 1])
