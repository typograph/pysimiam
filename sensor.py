#
# Sensors
#
# In the original Sim.I.Am code there is no base class, as the sensors are
# completely arbitrary objects
#

import random

class Sensor:
    @classmethod
    def addGaussNoise(value, sigma):
        """Returns the value with an added normal noise
        
        The return value is normally distributed around value with a standard deviation sigma
        """
        return random.gauss(value,sigma)
  
class InternalSensor(SimObject):
    def __init__(self,pose,robot):
        super().__init__(pose)
        self.__robot = robot
       
    def Pose(self):
        return super().Pose() + self.__robot.Pose()
    
    
