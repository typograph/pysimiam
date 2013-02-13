from simobject import SimObject

class Robot(SimObject):
    def pose_after(self,dt):
        """
        Returns the pose of the robot after time dt
        """
        pass

    def move_to(self,pose):
        self.set_pose(pose)
        
    def get_external_sensors(self):
        pass

    def update_sensors(self, other_object = None):
        """
        Update robots's sensors relative to a given object
        
        Parameters: other_object - other SimObject, if None
                    is passed, the sensors will be reset
        """
        pass
