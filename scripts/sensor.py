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
    def addGaussNoise(value, sigma):
        """Returns the value with an added normal noise
        
        The return value is normally distributed around value with a standard deviation sigma
        """
        return random.gauss(value,sigma)
  
class InternalSensor(SimObject):
    def __init__(self,pose,robot):
        super(InternalSensor, self).__init__(pose)
        self.__robot = robot
       
    def Pose(self):
        return super().Pose() + self.__robot.Pose()
    
class ProximitySensor(InternalSensor):
    def __init__(self,pose,robot):
        super(ProximitySensor, self).__init__(pose,robot)
        
    def distance(self):
        pass

class IRSensor(ProximitySensor):
    pass
