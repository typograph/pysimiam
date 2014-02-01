from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt

import pyqtgraph as pg
from random import randint

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

def get_color(color):
    if color is None:
        color = 'random'
    if isinstance(color,str):
        if color == 'random':
            return (randint(0,0xFF),randint(0,0xFF),randint(0,0xFF))
        elif color == 'black':
            return 0
        elif color == 'blue':
            return 'b'
        elif color == 'red':
            return 'r'
        elif color == 'green':
            return 'g'
    elif isinstance(color,tuple) or isinstance(color,list):
        if sum(color) <= 4.0:
            return [int(0xFF*c) for c in color]
        else:
            return color
    else:
        color = int(0xFF*float(color))
        return (color,color,color)
        
class PlotVariable:
    """
    A plot variable corresponds to one curve on the plot.
    It keeps track of the generating expression and of the
    values of the expression over time.
    """
    def __init__(self,label,expression,plot,color = None):
        self.expression = expression
        self.xdata = []
        self.ydata = []
        self.curve = plot.plot(name=label,pen=get_color(color))
        
    def add_point(self,x,y):
        self.xdata.append(x)
        self.ydata.append(y)
        self.curve.setData(self.xdata,self.ydata)

    def clear_data(self):
        self.xdata = []
        self.ydata = []
        self.curve.setData()

class Plot:
    """
    The plot follows one or more variables through time.
    It keeps track of the variables.
    """
    def __init__(self,plot):
        self.plot = plot
        plot.enableAutoRange('y',0.95)
        plot.addLegend()
        plot.setMouseEnabled(x=False, y=True)
        self.variables = []
    
    def add_curve(self,label,expression,color=None):
        self.variables.append(PlotVariable(label,expression,self.plot,color))
        
    def add_data(self,data):
        
        for variable in self.variables:
            if variable.expression not in data:
                print "No value for {}".format(variable.expression)
            else:
                variable.add_point(data['time'], data[variable.expression])
        self.plot.setXRange(max(0,data['time']-10),data['time'])
                
    def clear_data(self):
        for v in self.variables:
            v.clear_data()

class PlotWindow(pg.GraphicsWindow):
    """
    The window consists of a figure with a nav toolbar and subplots.
    It keeps track of all subplots
    """
    
    def __init__(self):
        pg.GraphicsWindow.__init__(self)

        self.plots = []
    
    #Slots
    def clear_data(self):
        for plot in self.plots:
            plot.clear_data()
        
    def add_plot(self):
        """Add a new subplot with a curve given by expression"""
        n = len(self.plots)
        if n > 0:
            self.nextRow()
        self.plots.append(Plot(self.addPlot()))
        if n > 0:
            self.plots[-1].plot.setXLink(self.plots[0].plot)
            
        return self.plots[-1]
    
    def add_data(self,data):
        for plot in self.plots:
            plot.add_data(data)

def create_predefined_plot_window(plots):
    """Create a window with plots from plot dictionary"""
    w = PlotWindow()
    es = []
    for plot in plots:
        p = w.add_plot()
        for l,e,c in plot:
            p.add_curve(l,e,c)        
            es.append(e)
    return es, w

#def create_plot_window(plotables):
    #"""Create a dialog for plot creation.
       #Return selected expressions
    #"""
    #dialog = PlotDialog(plotables)
    #if dialog.exec_():
        ## Create plots
        #return dialog.expressions(), dialog.plot()
    #return None, None

#class PlotableComboBox(QtGui.QComboBox):
    #def __init__(self,plotables,parent):
        #QtGui.QComboBox.__init__(self,parent)
        #self.plotables = plotables
        #for label in plotables:
            #self.addItem(label)
        #self.setEditable(True)
        #self.setCurrentIndex(0)
    
    #def expression(self):
        #text = str(self.currentText())
        #if text not in self.plotables:
            #return text
        #return self.plotables[text]
    
    #def create_curve(self,plot):
        #plot.add_curve(str(self.currentText()),self.expression())
    
#class SubPlotGroup(QtGui.QGroupBox):
    #def __init__(self,plotables,parent):
        #QtGui.QGroupBox.__init__(self,"Subplot",parent)
        #self.plotables = plotables
        #self.combos = []
        
        #self.vl = QtGui.QVBoxLayout(self)
        #button = QtGui.QPushButton("Add curve",self)
        #button.clicked.connect(self.add_curve)
        #self.vl.addWidget(button)
        #self.add_curve()
        
    #def add_curve(self):
        #self.combos.append(PlotableComboBox(self.plotables,self))
        #self.vl.insertWidget(len(self.combos)-1,self.combos[-1])
    
    #def expressions(self):
        #return [c.expression() for c in self.combos]
    
    #def create_plot(self,plot):
        #splot = plot.add_plot()
        #for combobox in self.combos:
            #combobox.create_curve(splot)

#class PlotDialog(QtGui.QDialog):
    #def __init__(self,plotables):
        #QtGui.QWidget.__init__(self)
        
        #self.plotables = plotables
        
        #self.vl = QtGui.QVBoxLayout(self)
        #self.plots = []
              
        #hl = QtGui.QHBoxLayout()

        #addplotbutton = QtGui.QPushButton("Add subplot",self)
        #addplotbutton.clicked.connect(self.add_subplot)
        #hl.addWidget(addplotbutton)
        #hl.addItem(
            #QtGui.QSpacerItem(40, 20,
                              #QtGui.QSizePolicy.Expanding,
                              #QtGui.QSizePolicy.Minimum))
                              
        #plotbutton = QtGui.QPushButton("Plot",self)
        #plotbutton.clicked.connect(self.accept)
        #hl.addWidget(plotbutton)

        #cancelbutton = QtGui.QPushButton("Cancel",self)
        #cancelbutton.clicked.connect(self.reject)
        #hl.addWidget(cancelbutton)

        #self.vl.addLayout(hl)
        
        #self.add_subplot()
     
    #def add_subplot(self):
        #self.plots.append(SubPlotGroup(self.plotables,self))
        #self.vl.insertWidget(len(self.plots)-1,self.plots[-1])
        
    #def expressions(self):
        #return [expr for plot in self.plots for expr in plot.expressions()]
    
    #def plot(self):
        #p = PlotWindow()
        #for plt in self.plots:
            #plt.create_plot(p)
        #return p