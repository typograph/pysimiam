#
# Class wxGCRenderer
#
# Implements Renderer for wxWidgets.
#

import numpy as np
import wx
from renderer import Renderer

class wxGCRenderer(Renderer):
    def __init__(self,DC):
        Renderer.__init__(self,DC.GetSizeTuple())
        self.dc = DC
        self.dc.SetAxisOrientation(True,True)
        self.gc = wx.GraphicsContext.Create(self.dc)
        self._pens = {}
        self._brushes = {}
        self.gc.PushState()

    def clearScreen(self):
        self.dc.Clear()

    def resetPose(self):
        """Resets the renderer to world coordinates
        """
        self.gc.PopState()
        self.gc.PushState()
    
    def setPose(self,pose):
        """Set a coordinate transformation based on the pose
        """
        self.resetPose()
        self.addPose(pose)
    
    def addPose(self,pose):
        """Add a pose transformation to the current transformation
        """
        self.gc.Translate(pose.x, pose.y)
        self.gc.Rotate(pose.theta)
        pass

    @staticmethod
    def __wxcolor(color):
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = (color) & 0xFF
        return wx.Colour(r,g,b,255)

    def setPen(self,color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        """
        if color not in self._pens:
            self._pens[color] = self.gc.CreatePen(wx.Pen(self.__wxcolor(color)))
        self.gc.SetPen(self._pens[color])       
        

    def setBrush(self,color):
        """Sets the fill color.

        Color is an integer interpreted as 0xRRGGBB.
        """
        if color not in self._brushes:
            self._brushes[color] = self.gc.CreateBrush(wx.Brush(self.__wxcolor(color)))
        self.gc.SetBrush(self._brushes[color])

    def drawPolygon(self,points):
        """Draws a polygon.
        
        Expects a list of points as a list of tuples or as a numpy array. Ignores Z if available
        """
        self.gc.DrawLines([point[:2] for point in points])
       
    def drawEllipse(self, x, y, w, h):
        """Draws an ellipse.
        """
        self.gc.DrawEllipse(x,y,w,h)

    def drawRectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        self.gc.DrawRectangle(x,y,w,h)

    def fillRectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        self.gc.DrawLines([(x,y),(x+w,y),(x+w,y+h),(x,y+h)])
        self.gc.DrawRectangle(x,y,w,h)
    
    def drawText(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        if bgcolor not in self._brushes:
            self._brushes[bgcolor] = self.gc.CreateBrush(wx.Brush(self.__wxcolor(bgcolor)))
        self.gc.DrawText(text,x,y,self._brushes[bgcolor])
    
    def drawLine(self, x1, y1, x2, y2):
        """Draws a line using the current pen from (x1,y1) to (x2,y2)
        """
        self.gc.DrawLines([(x1,y1),(x2,y2)])