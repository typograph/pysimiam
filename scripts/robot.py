from simobject import SimObject

class Robot(SimObject):
    def poseAfter(self,dt):
        """
        Returns the pose of the robot after time dt
        """
        pass
    
    def moveTo(self,pose):
        self.setPose(pose)

