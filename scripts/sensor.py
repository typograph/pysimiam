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
    @classmethod
    def add_gauss_noise(value, sigma):
        """Returns the value with an added normal noise
        
        The return value is normally distributed around value with a standard deviation sigma
        """
        return random.gauss(value,sigma)
  
class MountedSensor(SimObject):
    def __init__(self,pose,frame):
        SimObject.__init__(self,pose)
        self.__frame = frame

    def get_internal_pose(self):
        return SimObject.get_pose(self)
       
    def get_pose(self):
        x, y, t = SimObject.get_pose(self)
        rx, ry, rt = self.__frame.get_pose()
        return Pose(rx+x*cos(rt)-y*sin(rt),ry+x*sin(rt)+y*cos(rt),t+rt)
    
class ProximitySensor(MountedSensor):
    def __init__(self,pose,robot,geometry):
        """Create a proximity sensor mounted on robot at pose. The geometry
        is a (rmin, rmax, angle) tuple
        """
        MountedSensor.__init__(self,pose,robot)
        self.rmin, self.rmax, self.phi = geometry
        self.pts = [(self.rmin*cos(self.phi/2),self.rmin*sin(self.phi/2)),
                    (self.rmax*cos(self.phi/2),self.rmax*sin(self.phi/2)),
                    (self.rmax*cos(self.phi/2),-self.rmax*sin(self.phi/2)),
                    (self.rmin*cos(self.phi/2),-self.rmin*sin(self.phi/2))]
                    
        self.__distance = 65536
        self.set_color(0x11FF5566)

    def get_envelope(self):
        return self.pts

    def distance_to_value(self,dst):
        raise NotImplementedError("ProximitySensor.distance_to_value")
        
    def distance(self):
        return self.__distance
    
    def reading(self):
        return self.distance_to_value(self.distance())

    def update_distance(self, sim_object = None):
        pass

    def draw(self, r):
        r.set_pose(self.get_pose())
        r.set_brush(self.get_color())
        r.draw_ellipse(0,0,min(1,self.rmin/2),min(1,self.rmin/2))
        r.draw_polygon(self.pts)
        
    def get_distance_to(self, sim_object):
        ox, oy, ot = self.get_pose()
        min_distance = None
        for px, py in self.get_contact_points(sim_object):
            distance = sqrt((px-ox)*(px-ox)+(py-oy)*(py-oy))
            if min_distance:
                if distance < min_distance:
                    min_distance = distance
            else: min_distance = distance
            # Test code - return contact point info
            print "Contact @({0},{1}) ~{2}".format(px, py, distance)
            #
        return min_distance
