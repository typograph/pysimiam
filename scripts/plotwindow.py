from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt, QObject, QEvent

from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavToolbar
from matplotlib.figure import Figure

class PlotVariable:
    """
    A plot variable corresponds to one curve on the plot.
    It keeps track of the generating expression and of the
    values of the expression over time.
    """
    def __init__(self,expression,axes):
        self.expression = expression
        self.xdata = []
        self.ydata = []
        self.curve = Line2D([],[])
        axes.add_line(self.curve)
        
    def add_point(self,x,y):
        self.xdata.append(x)
        self.ydata.append(y)
        self.curve.set_data(self.xdata, self.ydata)

class Plot:
    """
    The plot follows one or more variables through time.
    It keeps track of the variables.
    """
    def __init__(self,expression,axes):
        self.axes = axes
        self.variables = []
        self.add_curve(expression)
    
    def add_curve(self,expression):
        self.variables.append(PlotVariable(expression,self.axes))
        
    def add_data(self,data):
        for variable in self.variables:
            if variable.expression not in data:
                print "No value for {}".format(variable.expression)
            else:
                variable.add_point(data['time'], data[variable.expression])

class PlotWindow(QtGui.QWidget):
    """
    The window consists of a figure with a nav toolbar and subplots.
    It keeps track of all subplots
    """
    
    def __init__(self, expression):
        QtGui.QWidget.__init__(self)

        self.plots = []

        self.figure = Figure()
        
        vlayout = QtGui.QVBoxLayout(self)

        canvas = FigureCanvas(self.figure)
        canvas.setParent(self)
        tbar = NavToolbar(canvas,self)

        vlayout.addWidget(tbar)
        vlayout.addWidget(canvas)
        
        self.add_plot(expression)
    
    #Slots
    def clear(self):
        self.plots = []
        self.figure.clf()
        
    def add_plot(self,expression):
        """Add a new subplot with a curve given by expression"""
        n = len(self.plots)
        if n > 0:
            for i, plot in enumerate(self.plots):
                plot.axes.change_geometry(n+1,1,i+1)
            self.plots.append(
                Plot(expression,
                     self.figure.add_subplot(n+1,1,n+1,sharex=self.plots[0].axes)))
        else:
            self.plots.append(Plot(expression, self.figure.add_subplot(111)))
        self.figure.canvas.draw()
    
    def add_data(self,data):
        for plot in self.plots:
            plot.add_data(data)
        self.figure.canvas.draw()
