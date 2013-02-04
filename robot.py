from simobject import SimObject

class Robot(SimObject):
    def PoseAfter(self,dt):
        """
        Returns the pose of the robot after time dt
        """
        pass
    
    def MoveTo(self,pose):
        self.__pose = pose

