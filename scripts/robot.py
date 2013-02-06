from simobject import SimObject

class Robot(SimObject):
    def pose_after(self,dt):
        """
        Returns the pose of the robot after time dt
        """
        pass

    def move_to(self,pose):
        self.set_pose(pose)

