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
        self._zoom = 1.0 # The zooming factor
        self._zoom_c = False # Whether the scaling is done from center
        self._show_grid = False # Show the grid
        self._dc_grid_pen = wx.Pen(wx.Colour(128,128,128,255),1,wx.SHORT_DASH)
        self._grid_spacing = 40.0 # default for unscaled
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
        self._grid_pen = self._gc.CreatePen(self._dc_grid_pen)
        
        self._gc.PushState() # The first pushed state is the default blank
        self._gc.PushState() # The second pushed state is the scaled one (zoom=1) with default pose
        self.__update_default_state()

    def show_grid(self, show=True):
        """Draw the grid on the canvas background.
        
        The grid is adaptive, with minimum interline distance of 10 px,
        and a maximum of 40 px.
        This method will clear the canvas
        """
        self._show_grid = show
        self.clear_screen()

    def __calculate_bounds(self):
        #transform = self._gc.CreateMatrix(*self._gc.GetTransform().Get())
        transform = self._gc.GetTransform()
        transform.Invert()
        xs,ys = zip(
                    transform.TransformPoint(0.0,0.0),
                    transform.TransformPoint(0.0,float(self.size[1])),
                    transform.TransformPoint(float(self.size[0]),float(self.size[1])),
                    transform.TransformPoint(float(self.size[0]),0.0)
                    )
        
        self.__bounds = (min(xs), min(ys), max(xs), max(ys))
        
        # Calculate grid coordinates
        xmin, ymin, xmax, ymax = self.__bounds
        
        # Determine min/max x & y line indices:
        x_ticks = (int(xmin//self._grid_spacing), int(xmax//self._grid_spacing + 1))
        y_ticks = (int(ymin//self._grid_spacing), int(ymax//self._grid_spacing + 1))
        
        transform.Invert()
        self.__grid_lines = [
            [transform.TransformPoint(xmin,i*self._grid_spacing) for i in range(*y_ticks)],
            [transform.TransformPoint(xmax,i*self._grid_spacing) for i in range(*y_ticks)],
            [transform.TransformPoint(i*self._grid_spacing,ymin) for i in range(*x_ticks)],
            [transform.TransformPoint(i*self._grid_spacing,ymax) for i in range(*x_ticks)]            
            ]
            
    def __draw_grid(self):
        self.reset_pose()
        self._gc.PushState()
        self._gc.SetTransform(self._gc.CreateMatrix())
        #self._gc.SetPen(self._grid_pen)
        self.set_pen(0x808080)
        self._gc.StrokeLineSegments(self.__grid_lines[0], self.__grid_lines[1])
        self._gc.StrokeLineSegments(self.__grid_lines[2], self.__grid_lines[3])
        self._gc.PopState()
        self.set_pen(None)

    def set_zoom_level(self, zoom_level):
        # Determine the right grid spacing for this zoom level
        self._grid_spacing *= zoom_level
        while self._grid_spacing > 80:
            self._grid_spacing /= 2
        while self._grid_spacing < 20:
            self._grid_spacing *= 2
        self._grid_spacing /= zoom_level
            
        print self._grid_spacing
            
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
        self.__calculate_bounds()
        self.clear_screen()

    def clear_screen(self):
        self._dc.Clear()
        if self._show_grid:
            self.__draw_grid()

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
