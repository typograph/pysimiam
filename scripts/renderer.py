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
        """Create a Renderer on canvas of size _size_.
        
        The default pen and brush are transparent
        """
        self.size = size
   
    def resetPose(self):
        """Reset the renderer to world coordinates
        """
        pass
    
    def setPose(self,pose):
        """Set a coordinate transformation based on the pose
        """
        self.resetPose()
        self.addPose(pose)
    
    def addPose(self,pose):
        """Add a pose transformation to the current transformation
        """
        pass

    def setPen(self,color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        Use None to unset a pen
        """
        pass        

    def setBrush(self,color):
        """Sets the fill color.

        Color is interpreted as 0xRRGGBB.
        Use None to unset a brush
        """
        pass
    
    def clearScreen(self):
        """Clears the canvas using the current brush
        """
        pass

    def drawLine(self, x1, y1, x2, y2):
        """Draws a line using the current pen from (x1,y1) to (x2,y2)
        """
        pass
    
    def drawEllipse(self, x, y, w, h):
        """Draws an ellipse with current pen and fills it with current brush.
        """
        pass

    def drawRectangle(self, x, y, w, h):
        """Draws a rectangle with current pen and fills it with current brush
        """
        pass
        
    def drawPolygon(self,points):
        """Draws a polygon with current pen and fills it with current brush
        
        Expects a list of points as a list of tuples or as a numpy array.
        """
        pass

    def drawText(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass