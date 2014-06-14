#
# (c) PySimiam Team
# 
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

import math
import numpy

from core.pose import Pose

from controllers.pid_controller import PIDController

class FollowWall(PIDController):
    """Follow walls is a controller that keeps a certain distance
    to the wall and drives alongside it in clockwise or counter-clockwise
    fashion. Works for the QuickBot robot.
    
    The constructor expects a list of sensor poses
    in the robot's frame of reference
    """
    def __init__(self, sensor_poses):
        '''Initialize internal variables'''
        PIDController.__init__(self)
        self.sensor_poses = sensor_poses

    def set_parameters(self, direction, distance, ks, v):
        """Set PID values, direction and distance.
        
        :param direction: The direction of wall following
        :type  direction: 'left' or 'right'
        :param distance: The desired distance to the wall to maintain
        :type  distance: float
        :param ks: PID gains
        :type  ks: (kp, ki, kd)
        :param v: Target speed
        :type  v: float
        """
        kp, ki, kd = ks
        PIDController.set_parameters(self, kp, ki, kd, v)

        self.direction = direction
        self.distance = distance
        
    def get_heading(self, sensor_distances):
        """Get the direction along the wall as a vector."""
        
        # Calculate vectors for the sensors
        if self.direction == 'left': # 0-2
            d, i = min( zip(sensor_distances[:3],[0,1,2]) )
            if i == 0 or (i == 1 and sensor_distances[0] <= sensor_distances[2]):
                i, j, k = 1, 0, 2
                
            else:
                i, j, k = 2, 1, 0
            
        else : # 2-4
            d, i = min( zip(sensor_distances[2:],[2,3,4]) )
            if i == 4 or (i == 3 and sensor_distances[4] <= sensor_distances[2]):
                i, j, k = 3, 4, 2
            else:
                i, j, k = 2, 3, 4
                
        p_front = Pose(sensor_distances[i]) >> self.sensor_poses[i]
        p_back = Pose(sensor_distances[j]) >> self.sensor_poses[j]

        self.vectors = [(p_front.x,p_front.y,1), (p_back.x, p_back.y, 1)]

        # Calculate the two vectors:
        ds = ((p_front.x-p_back.x)**2 + (p_front.y-p_back.y)**2)
        ms = (p_front.x*p_back.y - p_front.y*p_back.x)
        self.to_wall_vector = numpy.array([(p_back.y-p_front.y)*ms/ds,(p_front.x-p_back.x)*ms/ds,1])
        self.along_wall_vector = numpy.array([p_front.x-p_back.x, p_front.y-p_back.y, 1])

        # Calculate and return the heading vector:
        offset = abs(ms/math.sqrt(ds)) - self.distance
        if offset > 0:
            return 0.3*self.along_wall_vector + 2 * offset * self.to_wall_vector
        else:
            return 0.3*self.along_wall_vector + 3 * offset * self.to_wall_vector
    
               