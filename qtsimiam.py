"""QtSimiam
Author: Tim Fuchs
Description: This is the top-level application for QtSimiam.
"""
import sys
sys.path.insert(0, './scripts')
from PyQt4 import QtGui, QtCore
import os
from qtrenderer import QtRenderer

import simulator as sim
import threading

BITMAP_WIDTH = 600
BITMAP_HEIGHT = 800

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam")
        self.resize(BITMAP_WIDTH,BITMAP_HEIGHT)
        
        self.__create_toolbar()
        self.__create_menu()
        self.__create_statusbar()
        # Create status bar with intro messages
        self.statusBar().showMessage("Welcome to QtSimiam") 
        
        
        scrollArea = QtGui.QScrollArea(self)
        self.setCentralWidget(scrollArea)
        viewer = SimulatorViewer()
        scrollArea.setWidget(viewer)
        scrollArea.setWidgetResizable(True)
        
        # create the simulator thread
        self.simulatorThread = sim.Simulator(viewer.renderer,viewer.updateBitmap)
        self.simulatorThread.start()

    def __create_toolbar(self):
        
        tbar = QtGui.QToolBar("Control",self)
        tbar.addAction(QtGui.QIcon("./res/image/arrow-left-double.png"),"Rewind")
        tbar.addAction(QtGui.QIcon("./res/image/arrow-right.png"),"Run")
        tbar.addAction(QtGui.QIcon("./res/image/media-playback-pause-7.png"),"Pause")
        self.addToolBar(tbar)

    def __create_menu(self):
        menu = QtGui.QMenuBar(self)
        self.setMenuBar(menu)
        
        file_menu = menu.addMenu("&File")
        file_menu.addAction(QtGui.QIcon.fromTheme("document-open"),
                            "Open Supervisor",
                            self.onOpen,
                            QtGui.QKeySequence(QtGui.QKeySequence.Open))
                            
        file_menu.addSeparator()
        file_menu.addAction(QtGui.QIcon.fromTheme("application-exit"),
                            "Exit",
                            self.close,
                            QtGui.QKeySequence(QtGui.QKeySequence.Quit)
                            ).setToolTip("Quit the Program")
                            
    def __create_statusbar(self):      
        self.setStatusBar(QtGui.QStatusBar())

    def closeEvent(self,event):
        self.simulatorThread.stop()
        self.simulatorThread.join()
        super(SimulationWidget,self).closeEvent(event)

    # Slots
    @QtCore.pyqtSlot()
    def onOpen(self):
        # Load new definition
        pass

#end PySimiamFrame class

class SimulatorViewer(QtGui.QFrame):
    def __init__(self, parent = None):
        super(SimulatorViewer, self).__init__(parent)
        self.__bitmap = QtGui.QPixmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        self.__blt_bitmap = QtGui.QPixmap(BITMAP_WIDTH,BITMAP_HEIGHT)
        self.renderer = QtRenderer(self.__blt_bitmap)
        self.lock = threading.Lock()
        # code for async calling of update
        self.update_ = self.metaObject().method(self.metaObject().indexOfMethod('update()'))

    def paintEvent(self, event):
        super(SimulatorViewer, self).paintEvent(event)
        self.lock.acquire()
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0,0,self.__blt_bitmap)
        self.lock.release()
        
    def updateBitmap(self):
        self.lock.acquire()
        painter = QtGui.QPainter(self.__bitmap)
        painter.drawPixmap(0,0,self.__blt_bitmap)
        #self.__bitmap = QtGui.QPixmap(self.__blt_bitmap)
        self.lock.release()
        self.update_.invoke(self,QtCore.Qt.QueuedConnection)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    app.exec_()
