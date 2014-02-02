from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt, QObject, QEvent
from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtLegend, QwtData, QwtPlotMagnifier, QwtPlotPanner

import numpy
from random import random

def get_color(color):
    if color is None:
        color = 'random'
    if isinstance(color,str):
        if color == 'random':
            return QtGui.QColor(randint(0,0xFF),randint(0,0xFF),randint(0,0xFF))
        elif color == 'black':
            return Qt.black
        elif color == 'blue':
            return Qt.blue
        elif color == 'red':
            return Qt.red
        elif color == 'green':
            return Qt.green
    elif isinstance(color,tuple) or isinstance(color,list):
        if sum(color) <= 4.0:
            return QtGui.QColor(*(int(0xFF*c) for c in color))
        else:
            return QtGui.QColor(*color)
    else:
        color = int(0xFF*float(color))
        return QtGui.QColor(color,color,color)

class ExpandableQwtData(QwtData):
    def __init__(self):
        QwtData.__init__(self)
        self.points = []
        
    def copy(self):
        return self
        
    def size(self):
        return len(self.points)
    
    def x(self,i):
        return self.points[i][0]
    
    def y(self,i):
        return self.points[i][1]
    
    def add_point(self,x,y):
        self.points.append((x,y))

class PlotVariable:
    """
    A plot variable corresponds to one curve on the plot.
    It keeps track of the generating expression and of the
    values of the expression over time.
    """
    def __init__(self,label,expression,plot,color = None):
        self.expression = expression
        self.data = ExpandableQwtData()
        self.curve = QwtPlotCurve(label)
        self.curve.setData(self.data)
        self.curve.setPen(QtGui.QPen(get_color(color)))
        self.curve.attach(plot)
        
        
    def add_point(self,x,y):
        self.data.add_point(x,y)

    def clear_data(self):
        self.data.clear_data()

class Plot(QwtPlot):
    """
    The plot follows one or more variables through time.
    It keeps track of the variables.
    """
    def __init__(self,parent):
        QwtPlot.__init__(self,parent)
        self.variables = []
        self.insertLegend(QwtLegend(self),QwtPlot.TopLegend)
        self.setCanvasBackground(Qt.white)
        self.magnifier = QwtPlotMagnifier(self.canvas())
        self.magnifier.setAxisEnabled(QwtPlot.xBottom,False)
        self.magnifier.setAxisEnabled(QwtPlot.yLeft,True)
        self.panner = QwtPlotPanner(self.canvas())
        self.panner.setAxisEnabled(QwtPlot.xBottom,False)
        self.panner.setAxisEnabled(QwtPlot.yLeft,True)
    
    def add_curve(self,label,expression,color=None):
        self.variables.append(PlotVariable(label,expression,self,color))
        
    def add_data(self,data):
        
        for variable in self.variables:
            if variable.expression not in data:
                print("No value for {}".format(variable.expression))
            else:
                variable.add_point(data['time'], data[variable.expression])
                
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
        self.setLayout(QtGui.QVBoxLayout())
    
    #Slots
    def clear_data(self):
        for plot in self.plots:
            plot.clear_data()

    def alignVAxis(self):
        if len(self.plots) > 1:
            axis_widget = self.plots[0].axisWidget(QwtPlot.yLeft)
            pen = QtGui.QPen(Qt.black, axis_widget.penWidth())
            font = axis_widget.font()
            maxExtent = 0
            for plot in self.plots:
                scale_draw = plot.axisScaleDraw(QwtPlot.yLeft)
                scale_draw.setMinimumExtent(0)

                extent = scale_draw.extent(pen,font)
                if extent > maxExtent:
                    maxExtent = extent
                    
            for plot in self.plots:
                plot.axisScaleDraw(QwtPlot.yLeft).setMinimumExtent(maxExtent)

    def add_plot(self):
        """Add a new empty subplot"""
        self.plots.append(Plot(self))
        self.layout().addWidget(self.plots[-1])
        self.alignVAxis()
        return self.plots[-1]
    
    def add_data(self,data):
        if self.plots:
            xInterval = (max(0,data['time']-10), data['time'])
            for plot in self.plots:
                plot.setAxisScale(QwtPlot.xBottom,*xInterval)
                plot.add_data(data)
            self.alignVAxis()
            for plot in self.plots:
                plot.replot()
            #self.update()
