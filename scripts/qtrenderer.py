#
# Renderer class for PyQt4
#
# A glue layer between SimObject and UI
# 
from numpy import degrees
from pose import Pose
from renderer import Renderer
from PyQt4.QtGui import QPainter,QColor,QPolygonF
from PyQt4.QtCore import QPointF,Qt

class QtRenderer(Renderer):
    def __init__(self, pd):
        """Creates a new renderer based on a QPaintDevice pd
        """
        self._defpose = Pose() # The pose in the bottom-left corner
        self._zoom = 1 # The zooming factor
        self._zoom_c = False # Whether the scaling is done from center
        Renderer.__init__(self, (pd.width(), pd.height()), pd)

    def set_canvas(self, canvas):
        """Tell the renderer to draw on canvas
        
        The type of canvas is implementation-dependent
        """
        self._paintdevice = canvas
        self._painter = QPainter(canvas)
        self._painter.setRenderHint(QPainter.Antialiasing)
        # invert the y axis
        self._painter.scale(1,-1)
        self._painter.translate(0,-canvas.height())
        
        self.set_pen(None)
        # push the default state
        self._painter.save()
        self._painter.save()
        
    def set_zoom(self, zoom_level):
        self._zoom = float(zoom_level)
        self.__update_default_state()
        
    def __update_default_state(self):
        self._painter.restore() # Reset state
        self._painter.restore() # Set zoom to 1     
        self._painter.save() # Re-save the zoom-1
        if self._zoom_c:
            self._painter.translate(self.size[0]/2,self.size[1]/2)
        self._painter.scale(self._zoom,self._zoom)
        self._painter.rotate(degrees(-self._defpose.theta))
        self._painter.translate(-self._defpose.x, -self._defpose.y)
        self._painter.save() # Save the zoomed state
        self.clear_screen()

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
   
    def clear_screen(self):
        self._painter.save()
        self._painter.resetTransform()
        self.set_pen(0xFFFFFF)
        self.set_brush(0xFFFFFF)
        self.draw_rectangle(0,0,self.size[0],self.size[1])        
        self._painter.restore()
   
    def __delete__(self):
        self._painter.restore()
        self._painter.restore()
   
    def reset_pose(self):
        """Resets the renderer to world coordinates
        """
        self._painter.restore()
        self._painter.save()
        
    def add_pose(self,pose):
        """Add a pose transformation to the current transformation
        """
        self._painter.translate(pose.x,pose.y)
        self._painter.rotate(degrees(pose.theta))

    @staticmethod
    def __qcolor(color):
        """Returns qcolor for a given ARGB color
        """
        c = QColor(color)
        if color > 0xFFFFFF:
            c.setAlpha((color >> 24) & 0xFF)
        return c

    def set_pen(self,color):
        """Sets the line color.
        
        Color is interpreted as 0xAARRGGBB.
        """
        if color is None:
            self._painter.setPen(Qt.NoPen)
        else:
            self._painter.setPen(self.__qcolor(color))

    def set_brush(self,color):
        """Sets the fill color.
        
        Color is interpreted as 0xAARRGGBB.
        """
        if color is None:
            self._painter.setBrush(Qt.NoBrush)
        else:
            self._painter.setBrush(self.__qcolor(color))
        
    def draw_polygon(self,points):
        """Draws a polygon.
        
        Expects a list of points as a list of tuples or as a numpy array.
        """
        self._painter.drawPolygon(QPolygonF([QPointF(*point[:2]) for point in points]))
        
    def draw_ellipse(self, x, y, w, h):
        """Draws an ellipse.
        """
        self._painter.drawEllipse(x,y,w,h)

    def draw_rectangle(self, x, y, w, h):
        """Draws a rectangle.
        """
        self._painter.drawRect(x,y,w,h)
        
    def draw_text(self, text, x, y, bgcolor = 0):
        """Draws a text string at the defined position.
        """
        pass
    
    def draw_line(self, x1, y1, x2, y2):
        """Draws a line using the current pen from (x1,y1) to (x2,y2)
        """
        pass