"""
Title: Pose
Author: Jonathan Whitten
Date: 03 FEB 2013
Comments:
The pose class allows for a posing of objects in 2D space
"""
import numpy as np

class Pose(object):
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        #Units in mm
        self.x = x 
        self.y = y  
        self.theta = theta 

    def set_pose(self, *args):
        """pose setter using another pose
        @param
        args[0] - Pose object 
        or
        args[0] - float x
        args[1] - float y
        args[2] - float z
        """
        if isinstance(args[0], Pose):
            self.x = args[0].x
            self.y = args[0].y
            self.theta = args[0].theta
        elif isinstance(args[0], float):
            self.x = args[0]
            self.y = args[1]
            self.theta = args[2]

    def get_pose_list(self):
        return [self.x, self.y, self.theta]

    def get_transformation_matrix(self):
        #Z-axis ccw rotation transformation matrix
        T = np.array([\
            [np.cos(self.theta), -np.sin(self.theta), 0.0],\
            [np.sin(self.theta), np.cos(self.theta), 0.0],\
            [0, 0, 1.0]])
        return T



#end class Pose

#To convert from degress to radians use np.radians(<list>)
#To convert from radians to degrees use np.degrees(<list>)
