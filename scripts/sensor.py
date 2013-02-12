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
  
class InternalSensor(SimObject):
    def __init__(self,pose,robot):
        SimObject.__init__(self,pose)
        self.__robot = robot

    def get_internal_pose(self):
        return SimObject.get_pose(self)
       
    def get_pose(self):
        x, y, t = SimObject.get_pose(self)
        rx, ry, rt = self.__robot.get_pose()
        return Pose(rx+x*cos(rt)-y*sin(rt),ry+x*sin(rt)+y*cos(rt),t+rt)
    
class ProximitySensor(InternalSensor):
    def __init__(self,pose,robot):
        InternalSensor.__init__(self,pose,robot)
        
    def distance(self):
        pass
        
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

class IRSensor(ProximitySensor):
    pass
