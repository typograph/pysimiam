#
# Sensors
#
# In the original Sim.I.Am code there is no base class, as the sensors are
# completely arbitrary objects
#

import random
from simobject import SimObject

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
       
    def get_pose(self):
        return super().get_pose() + self.__robot.get_pose()
    
class ProximitySensor(InternalSensor):
    def __init__(self,pose,robot):
        InternalSensor.__init__(self,pose,robot)
        
    def distance(self):
        pass

class IRSensor(ProximitySensor):
    pass
