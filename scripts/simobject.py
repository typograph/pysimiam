import wx

class SimObject(object):
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
    
    def draw(self,gc):
        if not isinstance(gc,wc.GraphicsContext):
            raise ValueError("Draw error, cannot draw on %s" % gc.__class__.__name__)
        
        gc.PushState()
        brush = gc.CreateBrush(wx.Brush(self.__color))
        gc.SetBrush(brush)
        gc.SetTransform(self.getPose().getGraphicsMatrix(gc))
        gc.DrawLines(self.envelope())
        gc.PopState()
        
    
