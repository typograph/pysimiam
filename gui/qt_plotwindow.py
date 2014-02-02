from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt

from random import randint
try:
    import pyqtgraph as pg
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    USE_PLOTS = True
    
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
    
except:
    USE_PLOTS = False
    print("The plotting library could not be loaded.")

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
                print("No value for {}".format(variable.expression))
            else:
                variable.add_point(data['time'], data[variable.expression])
        self.plot.setXRange(max(0,data['time']-10),data['time'])
                
    def clear_data(self):
        for v in self.variables:
            v.clear_data()

def create_predefined_plot_window(plots):
    """Create a window with plots from plot dictionary"""
    if not USE_PLOTS:
        return None, None
    w = PlotWindow()
    es = []
    for plot in plots:
        p = w.add_plot()
        for l,e,c in plot:
            p.add_curve(l,e,c)        
            es.append(e)
    return es, w