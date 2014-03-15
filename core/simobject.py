from math import sin, cos, sqrt
from . import pylygon
from .pose import Pose

class SimObject:
    """The base class for all objects that can be drawn in the simulator. 
       Every SimObject has a pose, an envelope and a color.

       :param pose: The position of the object.
       :type pose: :class:`~pose.Pose`
       :param color: The internal color of the object (`0xAARRGGBB` or `0xRRGGBB`).
                     The default color is black.
       :type color: int
       """

    def __init__(self, pose, color = 0):
        """Create an object at *pose* with *color*
        """
        self.set_color(color)
        self.set_pose(pose)

    def get_color(self):
        """Get the internal color of the object"""
        return self.__color
    
    def set_color(self, color):
        """Set the internal color of the object"""
        self.__color = color

    def get_pose(self):
        """Get the pose of the object in world coordinates"""
        return self.__pose

    def set_pose(self,pose):
        """Set the pose of the object in world coordinates"""
        self.__world_envelope = None
        self.__pose = pose

    def draw(self, renderer):
        """Draws the object using *renderer* (see :class:`~renderer.Renderer`).
        
        The object doesn't have to use only one color. It doesn't even
        have to use its internal color while drawing.
        """
        raise NotImplementedError("SimObject.draw")
    
    def get_envelope(self):
        """Get the envelope of the object in object's local coordinates.
        
           The envelope is a list of *xy* pairs, describing the shape of the
           bounding polygon.
        """
        raise NotImplementedError("SimObject.get_envelope")
    
    def get_world_envelope(self, recalculate=False):
        """Get the envelope of the object in world coordinates.
           Used for checking collision.
           
           The envelope is cached, and will be recalculated if *recalculate*
           is `True`.
        """
        if self.__world_envelope is None or recalculate:
            x,y,t = self.get_pose()
            self.__world_envelope = [(x+p[0]*cos(t)-p[1]*sin(t),
                                      y+p[0]*sin(t)+p[1]*cos(t))
                                     for p in self.get_envelope()]
        return self.__world_envelope
    
    def get_bounding_rect(self):
        """Get the smallest rectangle that contains the object
           as a tuple (x, y, width, height)."""
        xmin, ymin, xmax, ymax = self.get_bounds()
        return (xmin,ymin,xmax-xmin,ymax-ymin)
    
    def has_collision(self, other):
        """Check if the object has collided with *other*.
        Return True or False"""
        self_poly = pylygon.Polygon(self.get_world_envelope())
        other_poly = pylygon.Polygon(other.get_world_envelope())
        
        # TODO: use distance() for performance
        #print("Dist:", self_poly.distance(other_poly))
        
        collision = self_poly.collidepoly(other_poly)
        if isinstance(collision, bool):
            if not collision: return False
        
        # Test code - print out collisions
        #print("Collision between {} and {}".format(self, other))
        # end of test code
        
        return True
    
    def get_contact_points(self, other):
        """Get a list of contact points with other object.
           Returns a list of (x, y)"""
        self_poly = pylygon.Polygon(self.get_world_envelope())
        other_poly = pylygon.Polygon(other.get_world_envelope())
        return self_poly.intersection_points(other_poly)

    def get_bounds(self):
        """Get the smallest rectangle that contains the object
           as a tuple (xmin, ymin, xmax, ymax)"""
        xs, ys = zip(*self.get_world_envelope())
        return (min(xs), min(ys), max(xs), max(ys))
            

class Polygon(SimObject):
    """The polygon is a simobject that gets the envelope supplied at construction.
       It draws itself as a filled polygon.
       
       :param pose: The position of the polygon.
       :type pose: :class:`~pose.Pose`
       :param shape: The list of points making up the polygon.
       :type shape: list((int,int))
       :param color: The color of the polygon (`0xAARRGGBB` or `0xRRGGBB`).
       :type color: int
       """
    def __init__(self, pose, shape, color):
        SimObject.__init__(self,pose, color)
        self.__shape = shape

    def get_envelope(self):
        return self.__shape

    def draw(self,r):
        """Draw the envelope (shape) filling it with the internal color."""
        r.set_pose(self.get_pose())
        r.set_brush(self.get_color())
        r.draw_polygon(self.get_envelope())

class Cloud(SimObject):
    """The cloud is a collection of points."""
    
    def __init__(self,color):
        SimObject.__init__(self, Pose(), color)
        self.points = []
    
    def add_point(self,pose):
        """Append a point at *pose* to the collection. The orientation of the pose is ignored"""
        self.points.append((pose.x,pose.y))

    def draw(self,r):
        """Draw a polyline with modes at all added points, using the internal color"""
        r.set_pose(self.get_pose()) # Reset everything
        r.set_pen(self.get_color())
        r.draw_points(self.points)
    
class Path(Cloud):
    """The path is a simobject that draws itself as a polyline.
       The line starts at `start`, and can be continued by adding
       points using :meth:`~simobject.Path.add_point`.
    
       :param start: The starting point of the polyline in world coordinates.
       :type start: :class:`~pose.Pose`
       :param color: The color of the line (`0xAARRGGBB` or `0xRRGGBB`).
       :type color: int
    
       The path is used by the simulator to track the history of robot motion.
       
       In the case that the Path is growing too long, it implements the 
       """
    L_crit = 10 # The length of the last path segment that stays 'exact'
    L_sway = 2  # Number of points from the simplified segment that are going to be simplified again

       
    def __init__(self, start, color):
        Cloud.__init__(self, color)
        
        self.simple_length = 0
        
        self.reset(start)

    @classmethod
    def RDP(cls,points):
        """An implementation of the Ramer-Douglas-Peucker algorithm
        to simplify long paths. At the moment throws away points that are
        less than two millimeters away from the straight line.
        """
        x_start, y_start = points[0]
        x_end, y_end = points[-1]
        dx = x_end - x_start
        dy = y_end - y_start
        dd = sqrt(dx*dx + dy*dy)
        
        if dd == 0:
            return [points[0]]
        
        dmax = 0
        imax = 0
        
        for i in range(1,len(points)-1):
            xi, yi = points[i]
            di = abs(dx*(y_start-yi) + dy*(xi-x_start))/dd
            if di > dmax:
                imax = i
                dmax = di
                
        if dmax < 0.001:
            return [points[0], points[-1]]
        else:
            return Path.RDP(points[:(imax+1)]) + Path.RDP(points[imax:])[1:]
        

    def add_point(self,pose):
        """Append a point at *pose* to the collection. The orientation of the pose is ignored"""
        if self.points and abs(pose.x - self.points[-1][0]) < 0.001 and abs(pose.y - self.points[-1][1]) < 0.001:
            return
        Cloud.add_point(self,pose)
        
        if len(self.points) - self.simple_length > 2*Path.L_crit:
            # Simplify the path leaving the last L_crit points intact
            self.points = self.points[:self.simple_length] + Path.RDP(self.points[self.simple_length:-Path.L_crit]) + self.points[-Path.L_crit:]
            self.simple_length = max(0,len(self.points) - Path.L_crit - Path.L_sway)

    def reset(self,start):
        """Set the start point to start.x and start.y
           and remove all other points"""
        self.points = [(start.x,start.y)]

    def draw(self,r):
        """Draw a polyline with modes at all added points, using the internal color"""
        r.set_pose(self.get_pose()) # Reset everything
        r.set_pen(self.get_color())
        for i in range(1,len(self.points)):
            x1,y1 = self.points[i-1]
            x2,y2 = self.points[i]
            r.draw_line(x1,y1,x2,y2)
