#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.week6 import FollowWall as FollowWallStub
import math
import numpy
from pose import Pose

class FollowWall(FollowWallStub):
    """Follow walls is a controller that keeps a certain distance
    to the wall and drives alongside it in clockwise or counter-clockwise
    fashion."""
    def __init__(self, params):
        '''Initialize internal variables'''
        FollowWallStub.__init__(self,params)
        
    def get_heading(self, state):
        """Get the direction along the wall as a vector."""
        
        # Week 6 Assignment:
        
        use_cached = False
        
        # Calculate vectors for the sensors
        if state.direction == 'left': # 0-2
            d, i = min( zip(state.sensor_distances[:3],[0,1,2]) )
            if i == 0 or (i == 1 and state.sensor_distances[0] <= state.sensor_distances[2]):
                i, j, k = 1, 0, 2
                
            else:
                i, j, k = 2, 1, 0
            
        else : # 2-4
            d, i = min( zip(state.sensor_distances[2:],[2,3,4]) )
            if i == 4 or (i == 3 and state.sensor_distances[4] <= state.sensor_distances[2]):
                i, j, k = 3, 4, 2
            else:
                i, j, k = 2, 3, 4
                
        p_front = Pose(state.sensor_distances[i]) >> self.sensor_poses[i]
        p_back = Pose(state.sensor_distances[j]) >> self.sensor_poses[j]

        self.vectors = [(p_front.x,p_front.y,1), (p_back.x, p_back.y, 1)]

        # Calculate the two vectors:
        ds = ((p_front.x-p_back.x)**2 + (p_front.y-p_back.y)**2)
        ms = (p_front.x*p_back.y - p_front.y*p_back.x)
        self.to_wall_vector = numpy.array([(p_back.y-p_front.y)*ms/ds,(p_front.x-p_back.x)*ms/ds,1])
        self.along_wall_vector = numpy.array([p_front.x-p_back.x, p_front.y-p_back.y, 1])

        # Calculate and return the heading vector:
        offset = abs(ms/math.sqrt(ds)) - state.distance
        if offset > 0:
            return 0.3*self.along_wall_vector + 2 * offset * self.to_wall_vector
        else:
            return 0.3*self.along_wall_vector + 3 * offset * self.to_wall_vector
    
        # End Week 6 Assignment
               