#
# Renderer class
#
# A glue layer between SimObject and UI
from pose import Pose
from math import tan, sqrt, atan2

class Renderer:
    """
        The Renderer class is an abstract class describing a generalized drawing engine.
        It has to be subclassed to implement the drawing in a way specific
        to the UI that the program is using.
        
        The base class does not impose any restrictions on the type of
        the *canvas* parameter. It is up to a specific implementation to
        interpret this parameter correctly.
    """
    
    def __init__(self, canvas):
        """Create a Renderer on canvas of size _size_.
        The default pen and brush are transparent
        """
        self._defpose = Pose() # The pose in the bottom-left corner
        self._zoom = 1.0 # The zooming factor
        self._zoom_c = False # Whether the scaling is done from center
        self._show_grid = False # Show the grid
        self._grid_spacing = 10.0 # default for unscaled
        self.__grid_subdiv = 1 # Current subdivision step
        self.__view_rect = None # The rect to keep in view
        
        self.size = None
        self.set_canvas(canvas)

    def __delete__(self):
        self.pop_state()
        self.pop_state()
    
    def show_grid(self, show=True):
        """Draw the grid on the canvas background by default.
        
        The grid is adaptive, with minimum interline distance of 40 px,
        and a maximum of 80 px. In the case the interline distance has to
        be smaller or larger, it is scaled. The interval is divided either
        in half, in five parts or in ten parts, to keep the grid decimal.
        
        This method will clear the canvas
        """
        self._show_grid = show
        self.clear_screen()
    
    def set_canvas(self, canvas):
        """Tell the renderer to draw on *canvas*.
        
        The type of canvas is implementation-dependent
        """
        self.set_pen(None)
        self.set_brush(None)
        self.push_state() # The first pushed state is the default blank
        self.push_state() # The second pushed state is the scaled one (zoom=1) with default pose
        self.reset_canvas_size(self._get_canvas_size(canvas))
        self._update_default_state()
   
    def reset_canvas_size(self,size):
        """Change canvas size
        
        On canvas rescale the zoom factor will be recalculated:
        If the view rect was set, the view will be rescaled to fit the rect.
        If the view rect was not set, the zoom factor and default pose will
        be kept.
        """
        self.size = size
        if self.__view_rect is not None:
            self.set_view_rect(*self.__view_rect)
    
    def _get_canvas_size(self,canvas):
        """Return the canvas size tuple (width,height)
        
        To be implemented in subclasses
        """
        raise NotImplementedError("Renderer._get_canvas_size")
    
    def push_state(self):
        """Store the current state on the stack.
        
        Current state includes default pose, pen and brush.
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.push_state")
    
    def pop_state(self):
        """Restore the last saved state from the stack

        The state includes default pose, pen and brush.
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.pop_state")
    
    def scale(self,factor):
        """Scale all drawing operations by *factor*
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.scale")
    
    def rotate(self, angle):
        """Rotate canvas by *angle* (in radians)
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.rotate")
    
    def translate(self, dx, dy):
        """Translate canvas by *dx*, *dy*
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.translate")

   
    def _calculate_bounds(self):
        """Store the bounds of the smallest rectangle containing the view \
        in ``self._bounds``.
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer._calculate_bounds")
   
    def _draw_grid(self):
        """Draw the grid on screen
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer._draw_grid")

    def set_screen_pose(self, pose):
        """ Set the pose of the lower-left corner of the canvas.
        
        The zoom center will switch to that corner.
        
        :param pose: The new pose of the lower-left corner.
        :type pose: :class:`~pose.Pose`
        
        """
        self._zoom_c = False
        self.__view_rect = None
        self._defpose = pose
        self._update_default_state()

    def set_screen_center_pose(self, pose):
        """ Set the pose of center of the canvas
        
        The zoom center will switch to canvas center.

        :param pose: The new pose of the lower-left corner.
        :type pose: :class:`~pose.Pose`
        """
        self._zoom_c = True
        self.__view_rect = None
        self._defpose = pose
        self._update_default_state()
   
    def _adjust_grid(self, zoom_level):
        """Calculate the right interline distance for *zoom_level*
        """
        self._grid_spacing *= zoom_level*self.__grid_subdiv
        while self._grid_spacing < 40:
            self._grid_spacing *= 10
        while self._grid_spacing >= 400: 
            self._grid_spacing /= 10
        for self.__grid_subdiv in [1,2,5]:
            if self._grid_spacing/self.__grid_subdiv < 80:
                break
        self._grid_spacing /= zoom_level*self.__grid_subdiv
   
    def set_zoom_level(self, zoom_level):
        """Zoom up the drawing by a factor of *zoom_level*
        
        The zoom center is at the last set screen pose.
        
        This method will clear the canvas.
        """
        self._adjust_grid(zoom_level)
        self.__view_rect = None
        self._zoom = float(zoom_level)
        self._update_default_state()
        
    def _update_default_state(self):
        """Calculate the default state with the current zoom level and pose
        
        This method will clear the canvas.
        """
        self.pop_state() # Reset state
        self.pop_state() # Set zoom to 1     
        self.push_state() # Re-save the zoom-1
        #print(self._zoom_c, self._defpose)
        if self._zoom_c:
            self.translate(self.size[0]/2,self.size[1]/2)
        self.scale(self._zoom)
        self.rotate(-self._defpose.theta)
        self.translate(-self._defpose.x, -self._defpose.y)
        self.push_state() # Save the zoomed state
        self._calculate_bounds()
        self.clear_screen()

    def scale_zoom_level(self, factor):
        """Zoom up the drawing by an additional *factor*
        
        Equivalent to ``set_zoom_level(zoom_level*factor)``
        
        The zoom center is at the last set screen pose.
        This method will clear the canvas.
        """
        self.set_zoom_level(self._zoom*factor)
    
    def set_view_rect(self, x, y, width, height):
        """Zoom on the rectangle to fit it into the view
        """
        self.__view_rect = (x,y,width,height)
        zoom = min(self.size[0]/float(width), self.size[1]/float(height))
        xtra_width = self.size[0]/zoom - float(width)
        xtra_height = self.size[1]/zoom - float(height)
        self._defpose = Pose(x - xtra_width/2, y - xtra_height/2, 0)
        self._zoom = zoom
        self._zoom_c = False
        self._adjust_grid(zoom)
        self._update_default_state()
       
    def reset_pose(self):
        """Resets the renderer to default pose and zoom level
        """
        self.pop_state()
        self.push_state()
    
    def set_pose(self, pose):
        """Set a coordinate transformation based on *pose*
        """
        self.reset_pose()
        self.add_pose(pose)

    def add_pose(self, pose):
        """Add a pose transformation to the current transformation
        """
        self.translate(pose.x, pose.y)
        self.rotate(pose.theta)

    def set_pen(self, color = 0, thickness = 1):
        """Sets the line color anf thickness.
        
        Color is interpreted as `0xAARRGGBB`. In case `AA == 0` the color
        is considered fully opaque.
        
        Use None to unset a pen.
        """
        raise NotImplementedError("Renderer.set_pen")

    def set_brush(self, color):
        """Sets the fill color.

        The color is an integer, interpreted as `0xAARRGGBB`.
        In the case `AA == 0` the color is considered fully opaque.
        
        Use `None` to unset a brush.
        """
        raise NotImplementedError("Renderer.set_brush")

    def clear_screen(self):
        """Clears the canvas and draws the grid if necessary
        
        To be implemented in subclasses.
        """
        if self._show_grid:
            self._draw_grid()

    def draw_point(self,x,y):
        """Draw a single point using the current pen at (x,y)"""
        raise NotImplementedError("Renderer.draw_point")
        
    def draw_points(self,points):
        """Draw a set of points, given as [(x,y)], using the current pen"""
        for x,y in points:
            self.draw_point(x,y)        

    def draw_line(self, x1, y1, x2, y2):
        """Draw a line using the current pen from (x1,y1) to (x2, y2)
        """
        raise NotImplementedError("Renderer.draw_line")
    
    def draw_arrow(self, x1, y1, x2, y2, angle=0.3, ratio=0.1, close=False):
        """Draw an arrow from (x1, y1) to (x2, y2).
           You can also specify the arrowhead angle (in radians), the ratio
           between arrowhead and arrow length and the triangular (close=True)
           or linear (close=False) arrowhead shape.
        """
        self.push_state()
        
        self.translate(x1,y1)
        self.rotate(atan2(y2-y1,x2-x1))
        self.scale(sqrt((x1-x2)**2 + (y1-y2)**2))
        
        xe = 1-ratio
        ye = tan(angle)*ratio
        self.draw_line(0,0,1,0)
        self.draw_line(1,0,xe,-ye)
        self.draw_line(1,0,xe,ye)
        if close:
            self.draw_line(xe,-ye,xe,ye)
            
        self.pop_state()
        
        

    def draw_ellipse(self, cx, cy, ra, rb=None):
        """Draws an ellipse with current pen and fills it with current brush.
        
        The center of the ellipse is at (*cx*, *cy*),
        the half-axes are *ra* and *rb*. In the case *rb* is not specified, 
        the method draws a circle of radius *ra*.
        """
        raise NotImplementedError("Renderer.draw_ellipse")

    def draw_rectangle(self, x, y, width, height):
        """Draws a rectangle with current pen and fills it with current brush
        
        The bottom-left corner of the rectangle is at (*x*, *y*),
        if the width and height are positive.
        """
        raise NotImplementedError("Renderer.draw_rectangle")

    def draw_polygon(self, points):
        """Draws a polygon with current pen and fills it with current brush
        
        Expects a list of points as a list of tuples or as a numpy array.
        """
        raise NotImplementedError("Renderer.draw_polygon")

    #def draw_text(self, text, x, y, bgcolor = 0):
        #"""Draws a text string at the defined position using the current brush
        #"""
        #raise NotImplementedError("Renderer.draw_text")
