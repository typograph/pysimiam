#
# Sensors
#
# In the original Sim.I.Am code there is no base class, as the sensors are
# completely arbitrary objects
#

import random
from simobject import SimObject
from pose import Pose
from math import sin, cos, sqrt

class Sensor:
    """Base superclass for sensor objects"""
    @classmethod
    def add_gauss_noise(value, sigma):
        """Returns the value with an added normal noise
        
        The return value is normally distributed around value with a standard deviation sigma
        """
        return random.gauss(value,sigma)
  
class MountedSensor(SimObject):
    """A subclass of sensor for skirt sensors"""
    def __init__(self,pose,frame):
        SimObject.__init__(self,pose)
        self.__frame = frame

    def get_internal_pose(self):
        """Get the pose of the sensor from simobject inheritance"""
        return SimObject.get_pose(self)
       
    def get_pose(self):
        x, y, t = SimObject.get_pose(self)
        rx, ry, rt = self.__frame.get_pose()
        return Pose(rx+x*cos(rt)-y*sin(rt),ry+x*sin(rt)+y*cos(rt),t+rt)
    
class ProximitySensor(MountedSensor):
    """Create a proximity sensor mounted on robot at pose. The geometry
    is a (rmin, rmax, angle) tuple
    """
    def __init__(self,pose,robot,geometry):
        """Create a proximity sensor mounted on robot at pose. The geometry
        is a (rmin, rmax, angle) tuple
        """
        MountedSensor.__init__(self,pose,robot)
        self.rmin, self.rmax, self.phi = geometry
        self.pts = self.get_cone(self.rmax)
        self.fullcone = self.pts
                    
        self.__distance = 65536
        self.set_color(0x33FF5566)

    def get_cone(self, distance):
        return [(self.rmin*cos(self.phi/2),self.rmin*sin(self.phi/2)),
                (distance*cos(self.phi/2),distance*sin(self.phi/2)),
                (distance*cos(self.phi/2),-distance*sin(self.phi/2)),
                (self.rmin*cos(self.phi/2),-self.rmin*sin(self.phi/2))]
        
    def get_envelope(self):
        """Return the envelope of the sensor"""
        return self.fullcone

    def distance_to_value(self,dst):
        """Returns the distance to the value using sensor calculations"""
        raise NotImplementedError("ProximitySensor.distance_to_value")
        
    def distance(self):
        """Returns the distance instance"""
        return self.__distance
    
    def reading(self):
        """Returns the reading value"""
        return self.distance_to_value(self.distance())

    def update_distance(self, sim_object = None):
        """updates all the distances from the reading"""
        if sim_object is None:
            # reset distance to max
            self.__distance = 65536
            self.set_color(0x33FF5566)
            self.pts = self.fullcone
            return True
        else:
            distance_to_obj = self.get_distance_to(sim_object)
            if distance_to_obj:
                if self.__distance > distance_to_obj:
                    #self.set_color(0x336655FF)
                    self.set_color(0xCCFF5566)
                    self.pts = self.get_cone(distance_to_obj)
                    self.__distance = distance_to_obj
                    return True
        return False

    def draw(self, r):
        """draws the sensor simobject"""
        r.set_pose(self.get_pose())
        r.set_brush(self.get_color())
        r.draw_ellipse(0,0,min(1,self.rmin/2),min(1,self.rmin/2))
        r.draw_polygon(self.pts)
        
    def get_distance_to(self, sim_object):
        """Gets the distance to another simobject"""
        ox, oy, ot = self.get_pose()
        min_distance = None
        for px, py in self.get_contact_points(sim_object):
            distance = sqrt((px-ox)*(px-ox)+(py-oy)*(py-oy))
            if min_distance is not None:
                if distance < min_distance:
                    min_distance = distance
            else: min_distance = distance
            # Test code - return contact point info
            #print "Contact @({0},{1}) ~{2}".format(px, py, distance)
            #
        return min_distance
