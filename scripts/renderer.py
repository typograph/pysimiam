#
# Renderer class
#
# A glue layer between SimObject and UI
#
# I realise this is a very simple renderer with very few functions,
# but I intend this to be just an example
#

class Renderer:
    def __init__(self,size):
        self.size = size

    def reset_pose(self):
        """Resets the renderer to world coordinates
        """
        pass

    def set_pose(self,pose):
        """Set a coordinate transformation based on the pose
        """
        pass

    def add_pose(self,pose):
        """Add a pose transformation to the current transformation
        """
        pass

    def set_pen(self,color):
        """Sets the line color.

        Color is interpreted as 0xRRGGBB.
        """
        pass

    def set_brush(self,color):
        """Sets the fill color.

        Color is interpreted as 0xRRGGBB.
        """
        pass

    def clear_screen(self):
        """Clears the canvas using the current brush
        """
        self.setBrush(0xFFFFFF)
        self.fillRectangle(0,0,self.size[0],self.size[1])

    def draw_polygon(self,points):
        """Draws a polygon.

        Expects a list of points as a list of tuples or as a numpy array.
        """
        pass

    def draw_ellipse(self, x, y, w, h):
        """Draws an ellipse.
        """
        pass

    def draw_rectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        pass

    def fill_rectangle(self, x, y, w, h):
        """Draws a rectangle with current pen and fills it with current brush
        """
        pass

    def draw_text(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass

    def draw_line(self, x1, y1, x2, y2):
        """Draw a line using the current pen from (x1,y1) to (x2, y2)
        """
            pass
