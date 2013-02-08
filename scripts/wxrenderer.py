#
# Class wxGCRenderer
#
# Implements Renderer for wxWidgets.
#

import numpy as np
from math import sin,cos
import wx
from renderer import Renderer
from pose import Pose

class wxGCRenderer(Renderer):
    def __init__(self, DC):
        self._defpose = Pose() # The pose in the bottom-left corner
        self._zoom = 1 # The zooming factor
        self._zoom_c = False # Whether the scaling is done from center
        Renderer.__init__(self,DC.GetSizeTuple(),DC)
        
    def set_canvas(self, DC):
        # Reset cached brushes & pens
        self._pens = {}
        self._brushes = {}
        
        # Set dc
        self._dc = DC
        self._gc = wx.GraphicsContext.Create(self._dc)
        
        self._gc.Scale(1,-1)
        self._gc.Translate(0, -self.size[1])
        
        self.set_pen(None)
        self.set_brush(None)
        
        self._gc.PushState() # The first pushed state is the default blank
        self._gc.PushState() # The second pushed state is the scaled one (zoom=1) with default pose
        self.__update_default_state()

    def set_zoom(self, zoom_level):
        self._zoom = float(zoom_level)
        self.__update_default_state()
        
    def __update_default_state(self):
        self._gc.PopState() # Reset state
        self._gc.PopState() # Set zoom to 1     
        self._gc.PushState() # Re-save the zoom-1
        if self._zoom_c:
            self._gc.Translate(self.size[0]/2,self.size[1]/2)
        self._gc.Scale(self._zoom,self._zoom)
        self._gc.Rotate(-self._defpose.theta)
        self._gc.Translate(-self._defpose.x, -self._defpose.y)
        self._gc.PushState() # Save the zoomed state
        self.clear_screen()

    def clear_screen(self):
        self._dc.Clear()

    def __set_scr_pose(self,pose):
        self._defpose = pose
        self.__update_default_state()
        self.clear_screen()

    def set_screen_pose(self, pose):
        self._zoom_c = False
        self.__set_scr_pose(pose)

    def set_screen_center_pose(self, pose):
        self._zoom_c = True
        self.__set_scr_pose(pose)

    def reset_pose(self):
        """Resets the renderer to default pose
        """
        self._gc.PopState()
        self._gc.PushState()
    
    #def set_pose(self, pose):
        #self.reset_pose()
        #self._gc.Translate(pose.x - self._defpose.x), pose.y - self._defpose.y)
        #self._gc.Rotate(pose.theta - self._defpose.theta)
    
    def add_pose(self, pose):
        """Add a pose transformation to the current transformation
        """
        self._gc.Translate(pose.x, pose.y)
        self._gc.Rotate(pose.theta)
        pass

    @staticmethod
    def __wxcolor(color):
        if color is None:
            return None
        r = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        b = (color) & 0xFF
        if color > 0xFFFFFF: # Opaque component
            o = (color >> 24) & 0xFF
        else:
            o = 0xFF
        return wx.Colour(r,g,b,o)

    def set_pen(self, color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        """
        if color not in self._pens:
            self._pens[color] = self._gc.CreatePen(wx.Pen(self.__wxcolor(color)))
        self._gc.SetPen(self._pens[color])       
        

    def set_brush(self, color):
        """Sets the fill color.

        Color is an integer interpreted as 0xRRGGBB.
        """
        if color not in self._brushes:
            self._brushes[color] = self._gc.CreateBrush(wx.Brush(self.__wxcolor(color)))
        self._gc.SetBrush(self._brushes[color])

    def draw_polygon(self, points):
        """Draws a polygon.

        Expects a list of points as a list of tuples or as a numpy array. Ignores Z if available
        """
        self.gc.DrawLines([point[:2] for point in points])
        xy_pts = [point[:2] for point in points]
        xy_pts.append(xy_pts[0])
        self._gc.DrawLines(xy_pts)
       
    def draw_ellipse(self, x, y, w, h):
        """Draws an ellipse.
        """
        self._gc.DrawEllipse(x,y,w,h)

    def draw_rectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        self._gc.DrawRectangle(x,y,w,h)
    
    def draw_text(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        if bgcolor not in self._brushes:
            self._brushes[bgcolor] = self._gc.CreateBrush(wx.Brush(self.__wxcolor(bgcolor)))
        self._gc.DrawText(text,x,y,self._brushes[bgcolor])
    
    def draw_line(self, x1, y1, x2, y2):
        """Draws a line using the current pen from (x1,y1) to (x2,y2)
        """
        self._gc.DrawLines([(x1,y1),(x2,y2)])
