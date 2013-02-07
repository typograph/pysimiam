"""
Title: Pose
Author: Jonathan Whitten
Date: 03 FEB 2013
Comments:
The pose class allows for a posing of objects in 2D space
"""
import numpy as np

class Pose(object):
    def __init__(self, *args):
        #Units in mm
        #convert to float just in case someone types an integer
        if len(args) == 0:
            self.set_pose(0,0,0)
        elif len(args) == 1:
            self.set_pose(*args[0])
        elif len(args) == 2:
            self.set_pose(args[0],args[1],0)
        elif len(args) == 3:
            self.set_pose(*args)
        else:
            raise ValueError("Invalid way to initialize a pose")

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
        elif len(args) == 3:
            self.x = float(args[0])
            self.y = float(args[1])
            self.theta = float(args[2])

    def get_pose_list(self):
        return [self.x, self.y, self.theta]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.theta

    def get_transformation_matrix(self):
        #Z-axis ccw rotation transformation matrix
        T = np.array([\
            [math.cos(self.theta), -math.sin(self.theta), self.x],\
            [math.sin(self.theta), math.cos(self.theta), self.y],\
            [0, 0, 1.0]])
        return T



#end class Pose

#To convert from degress to radians use np.radians(<list>)
#To convert from radians to degrees use np.degrees(<list>)
