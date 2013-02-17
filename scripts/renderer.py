#
# Renderer class
#
# A glue layer between SimObject and UI
from pose import Pose

class Renderer:
    """Superclass for interfacing the python simulator to different UI graphics context"""
    def __init__(self, canvas):
        """Create a Renderer on canvas of size _size_.
        The default pen and brush are transparent
        """
        self._defpose = Pose() # The pose in the bottom-left corner
        self._zoom = 1.0 # The zooming factor
        self._zoom_c = False # Whether the scaling is done from center
        self._show_grid = False # Show the grid
        self._grid_spacing = 40.0 # default for unscaled
        self.__view_rect = None # The rect to keep in view
        
        self.size = None
        self.set_canvas(canvas)

    def __delete__(self):
        self.pop_state()
        self.pop_state()
    
    def show_grid(self, show=True):
        """Draw the grid on the canvas background.
        
        The grid is adaptive, with minimum interline distance of 20 px,
        and a maximum of 80 px.
        This method will clear the canvas
        """
        self._show_grid = show
        self.clear_screen()
    
    def set_canvas(self, canvas):
        """Tell the renderer to draw on canvas
        
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
        """Scale drawing operations by factor
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.scale")
    
    def rotate(self, angle):
        """Rotate canvas by angle (in radians)
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.rotate")
    
    def translate(self, dx, dy):
        """Translate canvas by dx, dy
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer.translate")

   
    def _calculate_bounds(self):
        """Store the bounds of the smallest rectangle containing the view \
        in self._bounds.
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer._calculate_bounds")
   
    def _draw_grid(self):
        """Draw the grid on screen
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Renderer._draw_grid")

    def set_screen_pose(self, pose):
        """ Set the pose of lower-left corner of the canvas
        
        Will automatically switch zoom center to said corner.
        """
        self._zoom_c = False
        self.__view_rect = None
        self._defpose = pose
        self._update_default_state()

    def set_screen_center_pose(self, pose):
        """ Set the pose of center of the canvas
        
        Will automatically switch zoom center to canvas center.
        """
        self._zoom_c = True
        self.__view_rect = None
        self._defpose = pose
        self._update_default_state()
   
    def set_zoom_level(self, zoom_level):
        """Zoom up the drawing by a factor of zoom_level
        
        The zoom center is at the last set screen pose.
        This method will clear the canvas.
        """
        self._grid_spacing *= zoom_level
        while self._grid_spacing > 80:
            self._grid_spacing /= 2
        while self._grid_spacing < 20:
            self._grid_spacing *= 2
        self._grid_spacing /= zoom_level

        self.__view_rect = None
        self._zoom = float(zoom_level)
        self._update_default_state()
        
    def _update_default_state(self):
        self.pop_state() # Reset state
        self.pop_state() # Set zoom to 1     
        self.push_state() # Re-save the zoom-1
        #print self._zoom_c, self._defpose
        if self._zoom_c:
            self.translate(self.size[0]/2,self.size[1]/2)
        self.scale(self._zoom)
        self.rotate(-self._defpose.theta)
        self.translate(-self._defpose.x, -self._defpose.y)
        self.push_state() # Save the zoomed state
        self._calculate_bounds()
        self.clear_screen()

    def scale_zoom_level(self, factor):
        """Zoom up the drawing by a factor of zoom_level
        
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
        self._update_default_state()
       
    def reset_pose(self):
        """Resets the renderer to default pose
        """
        self.pop_state()
        self.push_state()
    
    def set_pose(self, pose):
        """Set a coordinate transformation based on the pose
        """
        self.reset_pose()
        self.add_pose(pose)

    def add_pose(self, pose):
        """Add a pose transformation to the current transformation
        """
        self.translate(pose.x, pose.y)
        self.rotate(pose.theta)

    def set_pen(self, color):
        """Sets the line color.
        Color is interpreted as 0xAARRGGBB. In case AA == 0 the color
        is considered fully opaque.
        Use None to unset a pen
        """
        raise NotImplementedError("Renderer.set_pen")

    def set_brush(self, color):
        """Sets the fill color.

        Color is interpreted as 0xAARRGGBB. In case AA == 0 the color
        is considered fully opaque.
        Use None to unset a brush
        """
        raise NotImplementedError("Renderer.set_brush")

    def clear_screen(self):
        """Clears the canvas using the current brush
        """
        if self._show_grid:
            self._draw_grid()

    def draw_line(self, x1, y1, x2, y2):
        """Draw a line using the current pen from (x1,y1) to (x2, y2)
        """
        raise NotImplementedError("Renderer.draw_line")

    def draw_ellipse(self, x, y, w, h):
        """Draws an ellipse with current pen and fills it with current brush.
        """
        raise NotImplementedError("Renderer.draw_ellipse")

    def draw_rectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        raise NotImplementedError("Renderer.draw_rectangle")

    def fill_rectangle(self, x, y, w, h):
        """Draws a rectangle with current pen and fills it with current brush
        """
        raise NotImplementedError("Renderer.fill_rectangle")
        
    def draw_polygon(self, points):
        """Draws a polygon with current pen and fills it with current brush
        Expects a list of points as a list of tuples or as a numpy array.
        """
        raise NotImplementedError("Renderer.draw_polygon")

    def draw_text(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        raise NotImplementedError("Renderer.draw_text")
