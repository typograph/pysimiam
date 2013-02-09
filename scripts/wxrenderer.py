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
        self._dc_grid_pen = wx.Pen(wx.Colour(128,128,128,255),1,wx.SHORT_DASH)
        Renderer.__init__(self,DC)
        
    def set_canvas(self, DC):
        # Reset cached brushes & pens
        self._pens = {}
        self._brushes = {}
        
        # Set dc
        self._dc = DC
        self._gc = wx.GraphicsContext.Create(self._dc)
        
        w, h = self._get_canvas_size(DC)
        
        # Set correct x & y axes directions
        self._gc.Scale(1,-1)
        self._gc.Translate(0, -h)
        
        self._grid_pen = self._gc.CreatePen(self._dc_grid_pen)
        
        Renderer.set_canvas(self,DC)
        
    def _get_canvas_size(self,DC):
        """Get the canvas size tuple (width,height)"""
        return DC.GetSizeTuple()

    def push_state(self):
        """Store the current state on the stack.
        
        Current state includes default pose, pen and brush
        """
        ### FIXME store brush
        self._gc.PushState()
    
    def pop_state(self):
        """Restore the last saved state from the stack

        The state includes default pose, pen and brush
        """
        ### FIXME store brush
        self._gc.PopState()

    def _calculate_bounds(self):
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
        self.__calculate_grid()
        
    def __calculate_grid(self):
        
        # Calculate grid coordinates
        xmin, ymin, xmax, ymax = self.__bounds
        
        # Determine min/max x & y line indices:
        x_ticks = (int(xmin//self._grid_spacing), int(xmax//self._grid_spacing + 1))
        y_ticks = (int(ymin//self._grid_spacing), int(ymax//self._grid_spacing + 1))
        
        transform = self._gc.GetTransform()
        self.__grid_lines = [
            [transform.TransformPoint(xmin,i*self._grid_spacing) for i in range(*y_ticks)],
            [transform.TransformPoint(xmax,i*self._grid_spacing) for i in range(*y_ticks)],
            [transform.TransformPoint(i*self._grid_spacing,ymin) for i in range(*x_ticks)],
            [transform.TransformPoint(i*self._grid_spacing,ymax) for i in range(*x_ticks)]            
            ]
            
    def _draw_grid(self):
        self.reset_pose()
        self._gc.PushState()
        self._gc.SetTransform(self._gc.CreateMatrix())
        #self._gc.SetPen(self._grid_pen)
        self.set_pen(0x808080)
        self._gc.StrokeLineSegments(self.__grid_lines[0], self.__grid_lines[1])
        self._gc.StrokeLineSegments(self.__grid_lines[2], self.__grid_lines[3])
        self._gc.PopState()
        self.set_pen(None)
        
    def scale(self, factor):
        """Scale drawing operations by factor
        
        To be implemented in subclasses.
        """
        self._gc.Scale(factor,factor)
    
    def rotate(self, angle):
        """Rotate canvas by angle (in radians)
        
        To be implemented in subclasses.
        """
        self._gc.Rotate(angle)
    
    def translate(self, dx, dy):
        """Translate canvas by dx, dy
        
        To be implemented in subclasses.
        """
        self._gc.Translate(dx,dy)

    def clear_screen(self):
        self._dc.Clear()
        Renderer.clear_screen(self)

    #def set_pose(self, pose):
        #self.reset_pose()
        #self._gc.Translate(pose.x - self._defpose.x), pose.y - self._defpose.y)
        #self._gc.Rotate(pose.theta - self._defpose.theta)
    
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

    def _async_call_draw_sim_objects(self,simobjs):
        """Asyncronously call __draw_sim_objects
        
        To be implemented in subclasses
        """
        wx.CallAfter(Renderer._draw_sim_objects, self, simobjs)
