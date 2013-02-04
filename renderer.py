#
# Renderer class
#
# A glue layer between SimObject and UI
# 
# I realise this is a very simple renderer with very few functions,
# but I intend this to be just an example
#

class Renderer:
    def __init__():
        pass
   
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
    
    def drawText(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass