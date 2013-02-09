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

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam")
        self.resize(400,400)
        
        self.__create_toolbars()
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

    def __create_toolbars(self):
        
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

        tbar = QtGui.QToolBar("View",self)
        a = tbar.addAction(QtGui.QIcon("./res/image/grid.png"),
                           "Show/Hide grid")
        a.triggered[bool].connect(self._show_grid)
        a.setCheckable(True)
        a.setChecked(False)
        
        zoom_group = QtGui.QActionGroup(tbar)
        a = tbar.addAction(QtGui.QIcon("./res/image/zoom-scene.png"),
                           "Show all",
                            self._zoom_scene)
        a.setCheckable(True)
        a.setChecked(True)
        zoom_group.addAction(a)
        
        a = tbar.addAction(QtGui.QIcon("./res/image/zoom-robot.png"),
                           "Follow robot",
                           self._zoom_robot)
        a.setCheckable(True)
        a.setChecked(False)
        zoom_group.addAction(a)

        self.__zoom_slider = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.__zoom_slider.setTickPosition(QtGui.QSlider.NoTicks)
        self.__zoom_slider.setMaximumWidth(300)
        self.__zoom_slider.setRange(-100,100)
        self.__zoom_slider.setValue(0)
        self.__zoom_slider.setEnabled(False)
        self.__zoom_slider.valueChanged[int].connect(self._scale_zoom)
        tbar.addWidget(self.__zoom_slider)
        
        self.__zoom_factor = 0
                       
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
            
    @QtCore.pyqtSlot(bool)
    def _show_grid(self,show):
        self._simulator_thread.show_grid(show)
            
    @QtCore.pyqtSlot()
    def _zoom_scene(self):
        self._simulator_thread.focus_on_world()
        self.__zoom_slider.setEnabled(False)

    @QtCore.pyqtSlot()
    def _zoom_robot(self):
        self._simulator_thread.focus_on_robot()
        self.__zoom_slider.setEnabled(True)
        self._simulator_thread.adjust_zoom(
            2.0**(self.__zoom_factor/60.0))        
            
    @QtCore.pyqtSlot(int)
    def _scale_zoom(self,value):
        self._simulator_thread.adjust_zoom(2.0**((value-self.__zoom_factor)/60.0))
        self.__zoom_factor = value
            
#end PySimiamFrame class

class SimulatorViewer(QtGui.QFrame):
    def __init__(self, parent = None):
        super(SimulatorViewer, self).__init__(parent)
        self.__bitmap = QtGui.QPixmap()
        self.__blt_bitmap = QtGui.QImage(self.size(), QtGui.QImage.Format_ARGB32)
        self.renderer = QtRenderer(self.__blt_bitmap)
        self.lock = threading.Lock()
        self.__resize_on_paint = False
        # code for async calling of update
        self.update_ = self.metaObject().method(self.metaObject().indexOfMethod('update()'))

    def paintEvent(self, event):
        super(SimulatorViewer, self).paintEvent(event)
        self.lock.acquire()
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(),QtCore.Qt.white)
        s = self.__bitmap.rect().size()
        s.scale(self.rect().size(),QtCore.Qt.KeepAspectRatio)
        dx = (self.width() - s.width())/2
        dy = (self.height() - s.height())/2
        painter.drawPixmap(QtCore.QRect(QtCore.QPoint(dx,dy),s),self.__bitmap,self.__bitmap.rect())
        self.lock.release()
        
    def update_bitmap(self):
        self.lock.acquire()
        self.__bitmap = QtGui.QPixmap.fromImage(self.__blt_bitmap)
        # resize the canvas - at this point nothing is being drawn
        if self.__resize_on_paint:
            self.__blt_bitmap = QtGui.QImage(self.width(),
                                            self.height(),
                                            QtGui.QImage.Format_ARGB32)
            self.renderer.set_canvas(self.__blt_bitmap)          
            self.__resize_on_paint = False
        self.lock.release()
        self.update_.invoke(self,QtCore.Qt.QueuedConnection)

    def resizeEvent(self,event):
        """Resize panel and canvas"""
        # use cached size and flag
        self.__resize_on_paint = True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    app.exec_()
