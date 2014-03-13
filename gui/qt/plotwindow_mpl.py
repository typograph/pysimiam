from PyQt4 import QtGui

from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavToolbar
from matplotlib.figure import Figure
import numpy
from random import random

def get_color(color):
    if color is None:
        color = random()
    if isinstance(color,str):
        if color == 'random':
            return (random(),random(),random())
        elif color == 'black':
            return (0,0,0)
        elif color == 'blue':
            return (0,0,1)
        elif color == 'red':
            return (1,0,0)
        elif color == 'green':
            return (0,1,0)
    elif isinstance(color,tuple) or isinstance(color,list):
        if sum(color) >= 4.0:
            return [c/255. for c in color]
        else:
            return color
    else:
        color = float(color)
        return (color,color,color)
    
class PlotVariable:
    """
    A plot variable corresponds to one curve on the plot.
    It keeps track of the generating expression and of the
    values of the expression over time.
    """
    def __init__(self,label,expression,axes,color = None):
        self.expression = expression
        #self.xdata = []
        #self.ydata = []
        self.ymax = float("-inf")
        self.ymin = float("inf")
        self.curve = Line2D([],[])
        self.curve.set_label(label)
        self.curve.set_color(get_color(color))
        axes.add_line(self.curve)
        
    def add_point(self,x,y):
        self.curve.set_xdata(numpy.append(self.curve.get_xdata(), x))
        self.curve.set_ydata(numpy.append(self.curve.get_ydata(), y))
        #self.xdata.append(x)
        #self.ydata.append(y)
        if y > self.ymax:
            self.ymax = y
        elif y < self.ymin or self.ymin is None:
            self.ymin = y            
        #self.curve.set_data(self.xdata, self.ydata)

    def clear_data(self):
        #self.xdata = []
        #self.ydata = []
        self.curve.set_data([],[])

class Plot:
    """
    The plot follows one or more variables through time.
    It keeps track of the variables.
    """
    def __init__(self,axes):
        self.axes = axes
        self.variables = []
    
    def add_curve(self,label,expression,color=None):
        self.variables.append(PlotVariable(label,expression,self.axes,color))
        self.axes.legend().draggable()
        
    def add_data(self,data):
        
        for variable in self.variables:
            if variable.expression not in data:
                print("No value for {}".format(variable.expression))
            else:
                variable.add_point(data['time'], data[variable.expression])
                
        ymin = min([v.ymin for v in self.variables])
        ymax = max([v.ymax for v in self.variables])
        
        # Add 5% axis margins
        drange = ymax-ymin
        if drange > 0:
            ymin -= 0.05*drange
            ymax += 0.05*drange
        
        self.axes.set_ylim(ymin,ymax)
                
    def clear_data(self):
        for v in self.variables:
            v.clear_data()

class PlotWindow(QtGui.QWidget):
    """
    The window consists of a figure with a nav toolbar and subplots.
    It keeps track of all subplots
    """
    
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.plots = []

        self.figure = Figure()
        
        vlayout = QtGui.QVBoxLayout(self)

        canvas = FigureCanvas(self.figure)
        canvas.setParent(self)
        tbar = NavToolbar(canvas,self)

        vlayout.addWidget(tbar)
        vlayout.addWidget(canvas)
    
    #Slots
    def clear_data(self):
        for plot in self.plots:
            plot.clear_data()
        
    def add_plot(self):
        """Add a new subplot with a curve given by expression"""
        n = len(self.plots)
        if n > 0:
            for i, plot in enumerate(self.plots):
                plot.axes.change_geometry(n+1,1,i+1)
            axes = self.figure.add_subplot(n+1,1,n+1,sharex=self.plots[0].axes)
        else:
            axes = self.figure.add_subplot(111)
            
        #axes.legend()
        
        self.plots.append(Plot(axes))
            
        self.figure.canvas.draw()
        return self.plots[-1]
    
    def add_data(self,data):
        for plot in self.plots:
            plot.add_data(data)
            plot.axes.set_xlim(right=data['time'])
            if data['time'] > 10:
                plot.axes.set_xlim(left=data['time']-10)
        self.figure.canvas.draw()