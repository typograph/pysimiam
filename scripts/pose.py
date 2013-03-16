import numpy as np

class Pose(object):
    """The pose class allows for a posing of objects in 2D space. The pose uses a right-hand coordinate system with counter-clockwise measurement of theta from the x-axis
    
    
       There are several ways to create a pose:
       
       =====================  =====================================
       ``Pose(x,y,theta)``    A pose at x,y and orientation `theta`
       ``Pose(x,y)``          Same as ``Pose(x,y,0)``
       ``Pose()``             Same as ``Pose(0,0,0)``
       ``Pose([x,y,theta])``  Same as ``Pose(x,y,theta)``
       =====================  =====================================
       
       There are several ways to access pose parameters::
       
            x, y, theta = pose
            x, y, theta = pose.get_list()
            x = pose.x; y = pose.y; theta = pose.theta
        
       """
    def __init__(self, *args):
        """Units in mm.  
        @param: args - (x, y, theta) tuple, Pose object, (x, y) tuple"""
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

    def set_pose(self, *args, **kwargs):
        """Set all or some pose parameters.
        
           Possible arguments are:
           
           =================================  ============================================
           ``set_pose(x, y, theta)``          Set all of x, y and theta
           ``set_pose(another_pose)``         Use x, y and theta from another pose
           ``set_pose(x = 3.0)``              Only change the x position
           ``set_pose(theta = pi, y = 3.0)``  Only change the y position and orientation
           =================================  ============================================
            """
        if len(args) == 3:
            self.x = float(args[0])
            self.y = float(args[1])
            self.theta = float(args[2])
        elif len(args) == 0:
            if 'x' in kwargs:
                self.x = float(kwargs['x'])
            if 'y' in kwargs:
                self.y = float(kwargs['y'])
            if 'theta' in kwargs:
                self.theta = float(kwargs['theta'])
        elif len(args) == 1 and isinstance(args[0], Pose):
            self.x = args[0].x
            self.y = args[0].y
            self.theta = args[0].theta
                

    def get_list(self):
        """Get the pose as a list ``[x, y, theta]``. Equivalent to ``list(pose)``."""
        return [self.x, self.y, self.theta]

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.theta

    def get_transformation(self):
        """Get the 3x3 transformation matrix associated with the pose."""
        #Z-axis ccw rotation transformation matrix
        T = np.array([\
            [np.cos(self.theta), -np.sin(self.theta), self.x],\
            [np.sin(self.theta), np.cos(self.theta), self.y],\
            [0, 0, 1.0]])
        return T

    def __str__(self):
        return "(%f,%f) %f" % (self.x,self.y,self.theta)

#end class Pose
