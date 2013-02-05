#
# Renderer class
#
# A glue layer between SimObject and UI
# 
# I realise this is a very simple renderer with very few functions,
# but I intend this to be just an example
#

class Renderer:
    def __init__(self,size):
        self.size = size
   
    def resetPose(self):
        """Resets the renderer to world coordinates
        """
        pass
    
    def setPose(self,pose):
        """Set a coordinate transformation based on the pose
        """
        pass
    
    def addPose(self,pose):
        """Add a pose transformation to the current transformation
        """
        pass

    def setPen(self,color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        """
        pass        

    def setBrush(self,color):
        """Sets the fill color.

        Color is interpreted as 0xRRGGBB.
        """
        pass
    
    def clearScreen(self):
        """Clears the canvas using the current brush
        """
        self.setBrush(0xFFFFFF)
        self.fillRectangle(0,0,self.size[0],self.size[1])

    def drawPolygon(self,points):
        """Draws a polygon.
        
        Expects a list of points as a list of tuples or as a numpy array.
        """
        pass
        
    def drawEllipse(self, x, y, w, h):
        """Draws an ellipse.
        """
        pass

    def drawRectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        pass
    
    def fillRectangle(self, x, y, w, h):    
        """Draws a rectangle with current pen and fills it with current brush
        """
        pass
    
    def drawText(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass