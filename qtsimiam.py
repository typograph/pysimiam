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

BITMAP_WIDTH = 400
BITMAP_HEIGHT = 400

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam")
        self.resize(BITMAP_WIDTH,BITMAP_HEIGHT)
        
        self.__create_toolbar()
        self.__create_menu()
        self.__create_statusbar()
        # Set intro message
        self.statusBar().showMessage("Welcome to QtSimiam") 
        
        # create XML file dialog
        self._world_dialog = QtGui.QFileDialog(self,
                                "Select World.xml File",
                                "worlds", 
                                "WorldFile (*.xml)")
        self._world_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        self._world_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)     

        # create supervisor file dialog
        self._supervisor_dialog = QtGui.QFileDialog(self,
                                     "Select Supervisor File",
                                     "supervisors", 
                                     "Supervisor (*.py)")
        self._supervisor_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        self._supervisor_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)     
        
        scrollArea = QtGui.QScrollArea(self)
        self.setCentralWidget(scrollArea)
        viewer = SimulatorViewer()
        scrollArea.setWidget(viewer)
        scrollArea.setWidgetResizable(True)
        
        # create the simulator thread
        self._simulator_thread = sim.Simulator(viewer.renderer,viewer.update_bitmap)
        self._simulator_thread.start()

    def __create_toolbar(self):
        
        tbar = QtGui.QToolBar("Control",self)
        tbar.addAction(QtGui.QIcon("./res/image/arrow-left-double.png"),
                       "Rewind",
                       self._on_rewind)
        tbar.addAction(QtGui.QIcon("./res/image/arrow-right.png"),
                       "Run",
                       self._on_run)
        tbar.addAction(QtGui.QIcon("./res/image/media-playback-pause-7.png"),
                       "Pause",
                       self._on_pause)
                       
        self.addToolBar(tbar)

    def __create_menu(self):
        menu = QtGui.QMenuBar(self)
        self.setMenuBar(menu)
        
        file_menu = menu.addMenu("&File")
        file_menu.addAction(QtGui.QIcon.fromTheme("document-open"),
                            "Open XML &World",
                            self._on_open_world,
                            QtGui.QKeySequence("Ctrl+W"))
        file_menu.addAction(QtGui.QIcon.fromTheme("document-open"),
                            "&Open Supervisor",
                            self._on_open,
                            QtGui.QKeySequence(QtGui.QKeySequence.Open))
                            
        file_menu.addSeparator()
        file_menu.addAction(QtGui.QIcon.fromTheme("application-exit"),
                            "E&xit",
                            self.close,
                            QtGui.QKeySequence(QtGui.QKeySequence.Quit)
                            ).setToolTip("Quit the Program")
                            
    def __create_statusbar(self):      
        self.setStatusBar(QtGui.QStatusBar())

    def closeEvent(self,event):
        self._simulator_thread.stop()
        self._simulator_thread.join()
        super(SimulationWidget,self).closeEvent(event)

    # Slots
    @QtCore.pyqtSlot()
    def _on_open(self):
        # Load new definition
        if self._supervisor_dialog.exec_():
            QtGui.QMessageBox.information(self,
                                          "Opening supervisor...",
                                          "Not implemented yet")

    @QtCore.pyqtSlot()
    def _on_rewind(self): # Start from the beginning
        self._simulator_thread.reset_simulation()

    @QtCore.pyqtSlot()
    def _on_run(self): # Run/unpause
        self._simulator_thread.start_simulation()

    @QtCore.pyqtSlot()
    def _on_pause(self): # Pause
        self._simulator_thread.pause_simulation()

    @QtCore.pyqtSlot()
    def _on_open_world(self):
        if self._world_dialog.exec_():
            self._simulator_thread.read_config(self._world_dialog.selectedFiles()[0])

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
        painter.drawPixmap(0,0,self.__bitmap)
        self.lock.release()
        
    def update_bitmap(self):
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
