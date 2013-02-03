class Pose:
    def __init__(self,x,y,theta):
        self.x = x
        self.y = y
        self.position = (x,y)
        self.orientation = theta
      
    def __place_pose(self,pose)
        """Returns _pose_ in coordinates of this pose
        
        The input pose is rotated and shifted according to this pose.
        """
        pass

    def __place_polygon(self,polygon)
        """Returns a polygon with a given pose
        
        The input polygon is rotated and shifted according to this pose.
        """
        pass
    
    def Place(self,obj):
        if isinstance(obj,Pose):
            return self.__place_pose(obj)
        else:
            return self.__place_polygon(obj)