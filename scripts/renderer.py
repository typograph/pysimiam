#
# Renderer class
#
# A glue layer between SimObject and UI
# 

class Renderer:
    def __init__(self, size):
        self.size = size
   
    def reset_pose(self):
        """Resets the renderer to world coordinates
        """
        pass
    
    def set_pose(self, pose):
        """Set a coordinate transformation based on the pose
        """
        self.reset_pose()
        self.add_pose(pose)
    
    def add_pose(self, pose):
        """Add a pose transformation to the current transformation
        """
        pass

    def set_pen(self, color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        """
        pass        

    def set_brush(self, color):
        """Sets the fill color.

        Color is interpreted as 0xRRGGBB.
        """
        pass
    
    def clear_screen(self):
        """Clears the canvas using the current brush
        """
        pass

    def draw_line(self, x1, y1, x2, y2):
        """Draws a line using the current pen from (x1,y1) to (x2,y2)
        """
        pass
    
    def draw_ellipse(self, x, y, w, h):
        """Draws an ellipse with current pen and fills it with current brush.
        """
        pass

    def draw_rectangle(self, x, y, w, h):
        """Draws a rectangle with current pen and fills it with current brush
        """
        pass
        
    def draw_polygon(self, points):
        """Draws a polygon with current pen and fills it with current brush
        
        Expects a list of points as a list of tuples or as a numpy array.
        """
        pass

    def draw_text(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass