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
        #super(wxGCRenderer, self).__init__()
        self.dc = wx.GCDC(DC)
        self.gc = self.dc.GetGraphicsContext()
        self._pens = {}
        self._brushes = {}
        
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

    @classmethod
    def __wxcolor(color):
        return wx.Colour("0x%.6X"%color)

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
        self.gc.DrawRectange(x,y,w,h)
    
    def drawText(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        if bgcolor not in self._brushes:
            self._brushes[bgcolor] = self.gc.CreateBrush(wx.Brush(self.__wxcolor(bgcolor)))
        self.gc.DrawText(text,x,y,self._brushes[bgcolor])
    
