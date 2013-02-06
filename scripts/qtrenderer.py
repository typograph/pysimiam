#
# Renderer class for PyQt4
#
# A glue layer between SimObject and UI
# 
from renderer import Renderer
from PyQt4.QtGui import QPainter,QColor,QPolygonF
from PyQt4.QtCore import QPointF,Qt

class QtRenderer(Renderer):
    def __init__(self,pd):
        """Creates a new renderer based on a QPaintDevice pd
        """
        Renderer.__init__(self,(pd.width(),pd.height()))
        self._paintdevice = pd
        self._painter = QPainter(pd)
        # invert the y axis
        self._painter.scale(1,-1)
        self._painter.translate(0,-pd.height())
        
        self.setPen(None)
        # push the default state
        self._painter.save()

    def clearScreen(self):
        self._painter.save()
        self._painter.resetTransform()
        self.setPen(0xFFFFFF)
        self.setBrush(0xFFFFFF)
        self.drawRectangle(0,0,self.size[0],self.size[1])        
        self._painter.restore()
   
    def __delete__(self):
        self._painter.restore()
   
    def resetPose(self):
        """Resets the renderer to world coordinates
        """
        self._painter.restore()
        self._painter.save()
        
    def addPose(self,pose):
        """Add a pose transformation to the current transformation
        """
        self._painter.translate(pose.x,pose.y)
        self._painter.rotate(pose.theta*57.2958)

    def setPen(self,color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        """
        if color is None:
            self._painter.setPen(Qt.NoPen)
        else:
            self._painter.setPen(QColor(color))

    def setBrush(self,color):
        """Sets the fill color.

        Color is interpreted as 0xRRGGBB.
        """
        if color is None:
            self._painter.setBrush(Qt.NoBrush)
        else:
            self._painter.setBrush(QColor(color))
    
    def drawPolygon(self,points):
        """Draws a polygon.
        
        Expects a list of points as a list of tuples or as a numpy array.
        """
        self._painter.drawPolygon(QPolygonF([QPointF(*point[:2]) for point in points]))
        
    def drawEllipse(self, x, y, w, h):
        """Draws an ellipse.
        """
        self._painter.drawEllipse(x,y,w,h)

    def drawRectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        self._painter.drawRect(x,y,w,h)
        
    def drawText(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass
    
    def drawLine(self, x1, y1, x2, y2):
        """Draws a line using the current pen from (x1,y1) to (x2,y2)
        """
        pass