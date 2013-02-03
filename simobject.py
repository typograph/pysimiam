import wx

class SimObject:
    def __init__(self,pose):
        self.__pose = pose
    
    def Pose(self):
        """Returns the pose of the object in world coordinates
        """
        return self.__pose
    
    def Draw(self,dc):
        """Draws the object on the passed DC
        """
        pass
    
    def Envelope(self):
        """The envelope of the object in object's local coordinates
        """
        ## At the moment the proposed format is a list of points
        pass

    def WorldEnvelope(self):
        """The envelope of the object combined with pose for easier collision testing
        """
        ## I assume a method Place for Pose
        return self.Pose().Place(self.Envelope())
        pass
    
class Obstacle(SimObject):
    def __init__(self,pose,shape,color):
        super().__init__(pose)
        self.__shape = shape
        self.__color = color
        
    def Envelope(self):
        return self.__shape
    
    def Draw(self,dc):
        dc.setBrush(wx.Brush(self.__color))
        dc.drawPolygon(self.WorldEnvelope())

class Robot(SimObject):
    def PoseAfter(self,dt):
        """
        Returns the pose of the robot after time dt
        """
        pass
    
    def MoveTo(self,pose):
        self.__pose = pose
    
class Khepera3(Robot):
    pass
    
    
### From here, not sure - maybe we shouldn't make sensors SimObjects

class Sensor(SimObject):
    def __init__(self,pose):
        super().__init__(pose)
    
    def __apply_noise(self,reading):
        """
        """
        pass
    
    def __distance2reading(self,dst):
        """Converts the distance (from Physics) to the output reading
        """
        pass
    
    def Reading(self):
        """Returns the IR signal
        """
        pass
    
    def Envelope(self):
        ## What is the envelope of a sensor?
        return [self.Pose().position]
    
class InternalSensor(SimObject):
    def __init__(self,pose,robot):
        super().__init__(pose)
        self.__robot = robot
       
    def Pose(self):
        return super().Pose() + self.__robot.Pose()
    
    