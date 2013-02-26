from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt, QObject, QEvent

from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavToolbar
from matplotlib.figure import Figure

from random import random

class PlotVariable:
    """
    A plot variable corresponds to one curve on the plot.
    It keeps track of the generating expression and of the
    values of the expression over time.
    """
    def __init__(self,label,expression,axes):
        self.expression = expression
        self.xdata = []
        self.ydata = []
        self.curve = Line2D([],[])
        self.curve.set_label(label)
        self.curve.set_color((random(),random(),random()))
        axes.add_line(self.curve)
        
    def add_point(self,x,y):
        self.xdata.append(x)
        self.ydata.append(y)
        self.curve.set_data(self.xdata, self.ydata)

    def clear_data(self):
        self.xdata = []
        self.ydata = []
        self.curve.set_data([],[])

class Plot:
    """
    The plot follows one or more variables through time.
    It keeps track of the variables.
    """
    def __init__(self,axes):
        self.axes = axes
        self.variables = []
    
    def add_curve(self,label,expression):
        self.variables.append(PlotVariable(label,expression,self.axes))
        self.axes.legend().draggable()
        
    def add_data(self,data):
        for variable in self.variables:
            if variable.expression not in data:
                print "No value for {}".format(variable.expression)
            else:
                variable.add_point(data['time'], data[variable.expression])
                
    def clear(self):
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
    def clear(self):
        for plot in self.plots:
            plot.clear()
        
    def add_plot(self):
        """Add a new subplot with a curve given by expression"""
        n = len(self.plots)
        if n > 0:
            for i, plot in enumerate(self.plots):
                plot.axes.change_geometry(n+1,1,i+1)
            axes = self.figure.add_subplot(n+1,1,n+1,sharex=self.plots[0].axes)
            axes.autoscale(True,'y')
        else:
            axes = self.figure.add_subplot(111)
            axes.autoscale(True)
            
        #axes.legend()
        
        self.plots.append(Plot(axes))
            
        self.figure.canvas.draw()
        return self.plots[-1]
    
    def add_data(self,data):
        for plot in self.plots:
            plot.add_data(data)
            plot.axes.relim()
            plot.axes.autoscale_view()
        self.figure.canvas.draw()

def create_plot_window(plotables):
    """Create a dialog for plot creation.
       Return selected expressions
    """
    dialog = PlotDialog(plotables)
    if dialog.exec_():
        # Create plots
        return dialog.expressions(), dialog.plot()
    return None

class PlotableComboBox(QtGui.QComboBox):
    def __init__(self,plotables,parent):
        QtGui.QComboBox.__init__(self,parent)
        self.plotables = plotables
        for label in plotables:
            self.addItem(label)
        self.setEditable(True)
        self.setCurrentIndex(0)
    
    def expression(self):
        text = str(self.currentText())
        if text not in self.plotables:
            return text
        return self.plotables[text]
    
    def create_curve(self,plot):
        plot.add_curve(str(self.currentText()),self.expression())
    
class SubPlotGroup(QtGui.QGroupBox):
    def __init__(self,plotables,parent):
        QtGui.QGroupBox.__init__(self,"Subplot",parent)
        self.plotables = plotables
        self.combos = []
        
        self.vl = QtGui.QVBoxLayout(self)
        button = QtGui.QPushButton("Add curve",self)
        button.clicked.connect(self.add_curve)
        self.vl.addWidget(button)
        self.add_curve()
        
    def add_curve(self):
        self.combos.append(PlotableComboBox(self.plotables,self))
        self.vl.insertWidget(len(self.combos)-1,self.combos[-1])
    
    def expressions(self):
        return [c.expression() for c in self.combos]
    
    def create_plot(self,plot):
        splot = plot.add_plot()
        for combobox in self.combos:
            combobox.create_curve(splot)

class PlotDialog(QtGui.QDialog):
    def __init__(self,plotables):
        QtGui.QWidget.__init__(self)
        
        self.plotables = plotables
        
        self.vl = QtGui.QVBoxLayout(self)
        self.plots = []
              
        hl = QtGui.QHBoxLayout()

        addplotbutton = QtGui.QPushButton("Add subplot",self)
        addplotbutton.clicked.connect(self.add_subplot)
        hl.addWidget(addplotbutton)
        hl.addItem(
            QtGui.QSpacerItem(40, 20,
                              QtGui.QSizePolicy.Expanding,
                              QtGui.QSizePolicy.Minimum))
                              
        plotbutton = QtGui.QPushButton("Plot",self)
        plotbutton.clicked.connect(self.accept)
        hl.addWidget(plotbutton)

        cancelbutton = QtGui.QPushButton("Cancel",self)
        cancelbutton.clicked.connect(self.reject)
        hl.addWidget(cancelbutton)

        self.vl.addLayout(hl)
        
        self.add_subplot()
     
    def add_subplot(self):
        self.plots.append(SubPlotGroup(self.plotables,self))
        self.vl.insertWidget(len(self.plots)-1,self.plots[-1])
        
    def expressions(self):
        return [expr for plot in self.plots for expr in plot.expressions()]
    
    def plot(self):
        p = PlotWindow()
        for plt in self.plots:
            plt.create_plot(p)
        return p