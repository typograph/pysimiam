import wx

class SimObject:
    def __init__(self,pose):
        self.__pose = pose
    
    def getPose(self):
        """Returns the pose of the object in world coordinates
        """
        return self.__pose
    
    def draw(self,dc):
        """Draws the object on the passed DC
        """
        pass
    
    def getEnvelope(self):
        """The envelope of the object in object's local coordinates
        """
        ## At the moment the proposed format is a list of points
        pass
    
class Polygon(SimObject):
    def __init__(self,pose,shape,color):
        super().__init__(pose)
        self.__shape = shape
        self.__color = color
        
    def envelope(self):
        return self.__shape
    
    def draw(self,r):
        r.setPose(self.Pose())
        r.setBrush(self.__color)
        r.drawPolygon(self.getEnvelope())
        
    