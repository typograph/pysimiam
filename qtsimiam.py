"""QtSimiam
Author: Tim Fuchs
Description: This is the top-level application for QtSimiam.
"""
import sys
sys.path.insert(0, './scripts')
from PyQt4 import QtGui, QtCore
import os
from qtrenderer import QtRenderer
from dockwindow import ParamDock

import simulator as sim
import threading

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam")
        self.resize(700,700)
        
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

        self.__paramwindows = {}
        self.__lastdock = None

        self.__sim_timer = QtCore.QTimer(self)
        self.__sim_timer.setInterval(100)
        self.__sim_timer.timeout.connect(self.__update_time)
        
        # create the simulator thread
        self._simulator_thread = sim.Simulator(viewer.renderer,
                                               viewer.update_bitmap,
                                               self.make_param_window)
        self._simulator_thread.start()

    def __create_toolbars(self):
        
        tbar = QtGui.QToolBar("Control",self)
        tbar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)
        
        self.__time_label = QtGui.QLabel("00:00.0",self)
        self.__time_label.setToolTip("Elapsed time")
        tbar.addWidget(self.__time_label)
        
        tbar.addAction(QtGui.QIcon("./res/image/arrow-left-double.png"),
                       "Rewind",
                       self._on_rewind)
        tbar.addAction(QtGui.QIcon("./res/image/arrow-right.png"),
                       "Run",
                       self._on_run)
        tbar.addAction(QtGui.QIcon("./res/image/media-playback-pause-7.png"),
                       "Pause",
                       self._on_pause)
        self.__speed_slider = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.__speed_slider.setToolTip("Adjust speed")
        self.__speed_slider.setTickPosition(QtGui.QSlider.NoTicks)
        self.__speed_slider.setMaximumWidth(300)
        self.__speed_slider.setRange(-100,100)
        self.__speed_slider.setValue(0)
        self.__speed_slider.setEnabled(False)
        self.__speed_slider.valueChanged[int].connect(self._scale_time)
        tbar.addWidget(self.__speed_slider)
        
        self.__speed_label = QtGui.QLabel(" Speed: 1.0x",self)
        self.__speed_label.setToolTip("Current speed multiplier")
        tbar.addWidget(self.__speed_label)
                       
        self.addToolBar(tbar)

        tbar = QtGui.QToolBar("View",self)
        tbar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)

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
        self.__zoom_slider.setToolTip("Adjust zoom")
        self.__zoom_slider.setMaximumWidth(300)
        self.__zoom_slider.setRange(-100,100)
        self.__zoom_slider.setValue(0)
        self.__zoom_slider.setEnabled(False)
        self.__zoom_slider.valueChanged[int].connect(self._scale_zoom)
        tbar.addWidget(self.__zoom_slider)
        self.__zoom_label = QtGui.QLabel(" Zoom: 1.0x",self)
        self.__zoom_label.setToolTip("Current zoom factor")
        tbar.addWidget(self.__zoom_label)
        
        self.__zoom_factor = 0
                       
        self.addToolBar(tbar)

    def __create_menu(self):
        menu = QtGui.QMenuBar(self)
        self.setMenuBar(menu)
        
        file_menu = menu.addMenu("&File")
        file_menu.addAction(QtGui.QIcon.fromTheme("document-open"),
                            "Open XML &World",
                            self._on_open_world,
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

    def make_param_window(self,robot_id,name,parameters):       
        if name in self.__paramwindows:
            self.__paramwindows[name].deleteLater()
            del self.__paramwindows[name]
            

        # FIXME adding to the right for no reason
        dock = ParamDock(self, robot_id, name, robot_id.get_color(), 
                         parameters, self._simulator_thread.apply_parameters)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
        if self.__lastdock is not None: # there are docks already
            self.tabifyDockWidget(self.__lastdock, dock)
        self.__paramwindows[name] = dock
        self.__lastdock = dock

    # Slots
    @QtCore.pyqtSlot()
    def _on_rewind(self): # Start from the beginning
        self.__sim_timer.stop()
        self.__time_label.setText("00:00.0")
        self._simulator_thread.reset_simulation()

    @QtCore.pyqtSlot()
    def _on_run(self): # Run/unpause
        self._simulator_thread.start_simulation()
        if self._simulator_thread.is_running():
            self.__sim_timer.start()
            self.__speed_slider.setEnabled(True)

    @QtCore.pyqtSlot()
    def _on_pause(self): # Pause
        self._simulator_thread.pause_simulation()
        if not self._simulator_thread.is_running():
            self.__sim_timer.stop()
            self.__speed_slider.setEnabled(False)

    @QtCore.pyqtSlot()
    def _on_open_world(self):
        self._on_pause()
        if self._world_dialog.exec_():
            for name, dock in self.__paramwindows.items():
                dock.deleteLater()
            self.__paramwindows = {}
            self.__lastdock = None
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
            5.0**(self.__zoom_factor/100.0))        
            
    @QtCore.pyqtSlot(int)
    def _scale_zoom(self,value):
        self._simulator_thread.adjust_zoom(5.0**((value-self.__zoom_factor)/100.0))
        self.__zoom_factor = value
        self.__zoom_label.setText(" Zoom: %.1fx"%(5.0**(value/100.0)))

    @QtCore.pyqtSlot(int)
    def _scale_time(self,value):
        m = 10.0**((value-self.__zoom_factor)/100.0)
        self._simulator_thread.set_time_multiplier(m)
        self.__speed_label.setText(" Speed: %.1fx"%m)

    @QtCore.pyqtSlot()
    def __update_time(self):
        t = self._simulator_thread.get_time()
        minutes = t//60
        self.__time_label.setText("%02d:%04.1f"%(minutes,t - minutes*60))
            
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
