#
# Renderer class
#
# A glue layer between SimObject and UI
from pose import Pose
from renderer import Renderer

class SubRenderer(Renderer):
    def __init__(self, canvas, x, y, width, height):
        """Create a Renderer on canvas of another renderer.
        x, y, width and height have values between 0 and 1 and are specified with respect to the original renderer.
        """
        self._clip = (x,y,width,height)
        Renderer.__init__(self,canvas)

    def __delete__(self):
        pass
       
    def set_canvas(self, canvas):
        """Tell the renderer to draw on canvas
        
        The type of canvas is implementation-dependent
        """
        self._renderer = canvas

        self.set_pen(None)
        self.set_brush(None)
        self.push_state() # The first pushed state is the default blank
        self.push_state() # The second pushed state is the scaled one (zoom=1) with default pose
        self.reset_canvas_size(self._get_canvas_size(canvas))
        self._update_default_state()
      
    def _get_canvas_size(self,canvas):
        """Return the canvas size tuple (width,height)
        
        To be implemented in subclasses
        """
        
        x, y, w, h = self._clip
        wp, hp = self._renderer.size
        return (w*wp, h*hp)
    
    def push_state(self):
        """Store the current state on the stack.
        
        Current state includes default pose, pen and brush.
        To be implemented in subclasses.
        """
        self._renderer.push_state()
    
    def pop_state(self):
        """Restore the last saved state from the stack

        The state includes default pose, pen and brush.
        To be implemented in subclasses.
        """
        self._renderer.pop_state()
    
    def scale(self,factor):
        """Scale drawing operations by factor
        
        To be implemented in subclasses.
        """
        self._renderer.scale(factor)
    
    def rotate(self, angle):
        """Rotate canvas by angle (in radians)
        
        To be implemented in subclasses.
        """
        self._renderer.rotate(angle)
    
    def translate(self, dx, dy):
        """Translate canvas by dx, dy
        
        To be implemented in subclasses.
        """
        self._renderer.translate(dx, dy)

   
    def _calculate_bounds(self):
        """Store the bounds of the smallest rectangle containing the view \
        in self._bounds.
        
        To be implemented in subclasses.
        """
        xminp, yminp, xmaxp, ymaxp = self._renderer._bounds
        self._bounds = 
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
        x, y, w, h = self._clip
        wp, hp = self._renderer.size
        self._renderer.set_pose(Pose(x*wp,y*hp,0))
        self._renderer.set_clip(0,0,w*wp,w*hp)

    def set_pen(self, color):
        """Sets the line color.
        Color is interpreted as 0xAARRGGBB. In case AA == 0 the color
        is considered fully opaque.
        Use None to unset a pen
        """
        self._rendere.set_pen(color)

    def set_brush(self, color):
        """Sets the fill color.

        Color is interpreted as 0xAARRGGBB. In case AA == 0 the color
        is considered fully opaque.
        Use None to unset a brush
        """
        self._renderer.set_brush(color)

    def clear_screen(self):
        """Clears the canvas using the current brush
        """
        self.reset_pose()
        self._renderer.clear_screen()
        Renderer.clear_screen(self)

    def draw_line(self, x1, y1, x2, y2):
        """Draw a line using the current pen from (x1,y1) to (x2, y2)
        """
        self._renderer.draw_line(x1, y1, x2, y2)

    def draw_ellipse(self, x, y, w, h):
        """Draws an ellipse with current pen and fills it with current brush.
        """
        self._renderer.draw_ellipse(x, y, w, h)

    def draw_rectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        self._renderer.draw_rectangle(x, y, w, h)

    def fill_rectangle(self, x, y, w, h):
        """Draws a rectangle with current pen and fills it with current brush
        """
        self._renderer.fill_rectangle(x, y, w, h)
        
    def draw_polygon(self, points):
        """Draws a polygon with current pen and fills it with current brush
        Expects a list of points as a list of tuples or as a numpy array.
        """
        self._renderer.draw_polygon(points)

    def draw_text(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        self._renderer.draw_text(text, x, y, bgcolor)
