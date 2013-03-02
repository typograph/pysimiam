from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal, Qt

import numpy
from random import random

from qt_plotwindow_mpl import PlotWindow
#from qt_plotwindow_qwt import PlotWindow
#from qt_plotwindow_qtgraph import PlotWindow

def create_plot_window(plotables):
    """Create a dialog for plot creation.
       Return selected expressions
    """
    dialog = PlotDialog(plotables)
    if dialog.exec_():
        # Create plots
        return dialog.expressions(), dialog.plot()
    return None

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