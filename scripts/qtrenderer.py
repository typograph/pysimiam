#
# Renderer class for PyQt4
#
# A glue layer between SimObject and UI
#
from numpy import degrees
from pose import Pose
from renderer import Renderer
from PyQt4.QtGui import QPainter,QColor,QPolygonF,QPen
from PyQt4.QtCore import QPointF,QLineF,Qt

class QtRenderer(Renderer):
    def __init__(self, pd):
        """Creates a new renderer based on a QPaintDevice pd
        """
        self._grid_pen = QPen(QColor(0x808080))
        self._grid_pen.setStyle(Qt.DashLine)
        Renderer.__init__(self, pd)

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

        Renderer.set_canvas(self,canvas)

    def _get_canvas_size(self,pd):
        """Get the canvas size tuple (width,height)"""
        return (pd.width(), pd.height())

    def push_state(self):
        """Store the current state on the stack.
        Current state includes default pose, pen and brush
        """
        ### FIXME store things
        self._painter.save()

    def pop_state(self):
        """Restore the last saved state from the stack
        The state includes default pose, pen and brush
        """
        ### FIXME store things
        self._painter.restore()

    def _calculate_bounds(self):
        transform = self._painter.worldTransform().inverted()[0]
        xs,ys = zip(
                    transform.map(0.0,0.0),
                    transform.map(0.0,float(self.size[1])),
                    transform.map(float(self.size[0]),float(self.size[1])),
                    transform.map(float(self.size[0]),0.0)
                    )

        self._bounds = (min(xs), min(ys), max(xs), max(ys))

    def _draw_grid(self):
        self.reset_pose()
        self._painter.setPen(self._grid_pen)
        xmin, ymin, xmax, ymax = self._bounds

        # Determine min/max x & y line indices:
        x_ticks = (int(xmin//self._grid_spacing), int(xmax//self._grid_spacing + 1))
        y_ticks = (int(ymin//self._grid_spacing), int(ymax//self._grid_spacing + 1))

        self._painter.drawLines(
            [QLineF(xmin, i * self._grid_spacing,
                    xmax, i * self._grid_spacing)
                for i in range(*y_ticks)])
        self._painter.drawLines(
            [QLineF(i * self._grid_spacing, ymin,
                    i * self._grid_spacing, ymax)
                for i in range(*x_ticks)])

    def scale(self, factor):
        """Scale drawing operations by factor
        To be implemented in subclasses.
        """
        self._painter.scale(factor,factor)

    def rotate(self, angle):
        """Rotate canvas by angle (in radians)
        To be implemented in subclasses.
        """
        self._painter.rotate(degrees(angle))

    def translate(self, dx, dy):
        """Translate canvas by dx, dy
        To be implemented in subclasses.
        """
        self._painter.translate(dx,dy)

    def clear_screen(self):
        self._painter.save()
        self._painter.resetTransform()
        self.set_pen(0xFFFFFF)
        self.set_brush(0xFFFFFF)
        self.draw_rectangle(0,0,self.size[0],self.size[1])
        self._painter.restore()
        Renderer.clear_screen(self)

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
