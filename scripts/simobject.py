from math import sin, cos
import pylygon

class SimObject:
    def __init__(self,pose):
        self.__pose = pose

    def get_pose(self):
        """Returns the pose of the object in world coordinates
        """
        return self.__pose

    def set_pose(self,pose):
        """Returns the pose of the object in world coordinates
        """
        self.__pose = pose

    def draw(self,dc):
        """Draws the object on the passed DC
        """
        pass
    
    def get_envelope(self):
        """The envelope of the object in object's local coordinates
        """
        ## At the moment the proposed format is a list of points
        pass
    
    def get_world_envelope(self):
        x,y,t = self.get_pose()
        return [(x+p[0]*cos(t)-p[1]*sin(t),y+p[0]*sin(t)+p[1]*cos(t))
                for p in self.get_envelope()]
    
    def get_bounding_rect(self):
        """Get the smallest rectangle that contains the object
        
        Returns a tuple (x,y,width,height)
        """
        xmin, ymin, xmax, ymax = self.get_bounds()
        return (xmin,ymin,xmax-xmin,ymax-ymin)
    
    def has_collision(self, other):
        """Check if the object has collided with other
        
        Return True or False
        """
        self_poly = pylygon.Polygon(self.get_world_envelope())
        other_poly = pylygon.Polygon(other.get_world_envelope())
        
        # TODO: use distance() for performance
        #print "Dist:", self_poly.distance(other_poly)
        
        collision = self_poly.collidepoly(other_poly)
        if isinstance(collision, bool):
            if not collision: return False
        
        # Test code - print out collisions
        print "Collision between {} and {}".format(self, other)
        # end of test code
        
        return True
        
    def get_contact_points(self, other):
        self_poly = pylygon.Polygon(self.get_world_envelope())
        other_poly = pylygon.Polygon(other.get_world_envelope())
        return self_poly.intersection_points(other_poly)

    def get_bounds(self):
        """Get the smallest rectangle that contains the object
        
        Returns a tuple (xmin,ymin,xmax,ymax)
        """
        xs, ys = zip(*self.get_world_envelope())
        return (min(xs), min(ys), max(xs), max(ys))
            

class Polygon(SimObject):
    def __init__(self,pose,shape,color):
        SimObject.__init__(self,pose)
        self.__shape = shape
        self.__color = color

    def get_envelope(self):
        return self.__shape

    def draw(self,r):
        r.set_pose(self.get_pose())
        r.set_brush(self.__color)
        r.draw_polygon(self.get_envelope())
