import numpy as np
from math import sin,cos,pi

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
    def __init__(self, *args, **kwargs):
        """Units in mm.  
        @param: args - (x, y, theta) tuple, Pose object, (x, y) tuple"""
        #Units in mm
        #convert to float just in case someone types an integer
        
        self.x, self.y, self.theta = 0,0,0
        self.set_pose(*args,**kwargs)
        
    def set_pose(self, *args, **kwargs):
        """Set all or some pose parameters.
        
           Possible arguments are:
           
           =================================  ============================================
           ``set_pose(x, y, theta)``          Set all of x, y and theta
           ``set_pose(another_pose)``         Use x, y and theta from another pose
           ``set_pose(x = 3.0)``              Only change the x position
           ``set_pose(theta = pi, y = 3.0)``  Only change the y position and orientation
           ``set_pose(another_pose, y = 1)``  Use x and theta from another pose, use y=1
           =================================  ============================================
            """
        if len(args) == 1 and isinstance(args[0], Pose):           
            self.x, self.y, self.theta = args[0]
        elif len(args) > 3:
            raise ValueError("Too many parameters for Pose")
        elif len(args) > 0:
            try:
                self.x, self.y, self.theta = args[0]
                if len(args) > 1:
                    raise ValueError("Too many parameters for Pose")
            except TypeError:
                self.x = float(args[0])
                if len(args) > 1:
                    self.y = float(args[1])
                if len(args) > 2:
                    self.theta = float(args[2])
        len_kw = len(kwargs)
        if 'x' in kwargs:
            self.x = float(kwargs['x'])
            len_kw -= 1
        if 'y' in kwargs:
            self.y = float(kwargs['y'])
            len_kw -= 1
        if 'theta' in kwargs:
            self.theta = float(kwargs['theta'])               
            len_kw -= 1
        if len_kw > 0:
            raise ValueError("Too many keyword parameters for Pose")

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
    
    def iscloseto(self,other,epsilon):
        """Compare this pose to *other*. Returns True if the relative distance
           in x, y and theta is smaller than *epsilon*
        """
        return (self.x - other.x)/(self.x + other.x) < epsilon \
           and (self.y - other.y)/(self.y + other.y) < epsilon \
           and (self.theta - other.theta)%(2*pi)/(2*pi) < epsilon
    
    def __eq__(self,other):
        if not isinstance(other,Pose):
            return NotImplemented
        return self.iscloseto(other,1e-8)
    
    def __rshift__(self,other):
        """A shifted Pose is the same pose in the coordinate system defined by the other pose.
           This operation is not commutative.
           
           If ``b`` is a pose in ``a`` frame of reference, ``b >> a`` is the same pose 
           if the frame of reference that ``a`` is defined.
           """
        if not isinstance(other,Pose):
            return NotImplemented
        rx, ry, rt = other
        return Pose(rx+self.x*cos(rt)-self.y*sin(rt),ry+self.x*sin(rt)+self.y*cos(rt),self.theta+rt)

    def __lshift__(self,other):
        """An unshifted Pose is the same pose in the local coordinate system of other pose.
           This operation is not commutative.
           
           If ``a`` and ``b`` are poses in the same frame of reference, then ``b << a``
           is ``b`` in ``a`` frame of reference.           
           """
        if not isinstance(other,Pose):
            return NotImplemented
        rx, ry, rt = other
        return Pose((self.x-rx)*cos(rt)+(self.y-ry)*sin(rt),-(self.x-rx)*sin(rt)+(self.y-ry)*cos(rt),self.theta-rt)

#end class Pose

# Testing

if __name__ == "__main__":
    a = Pose(1,2,3)
    b = Pose(6,7,8)
    c = Pose(1,2,3)
    print(a==c)
    print(b)
    print(b << a)
    print(b >> a)
    print((b >> a) << a == b)
    print((b << a) >> a == b)
    