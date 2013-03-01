#!/usr/bin/python
#QtSimiam
#Author: Tim Fuchs
#Description: This is the top-level application for QtSimiam.
import sys
sys.path.insert(0, './scripts')
from PyQt4 import QtGui, QtCore
import os
from qtrenderer import QtRenderer
from dockwindow import ParamDock, DockManager

import simulator as sim
import Queue as queue
from traceback import format_exception

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam")
        self.resize(700,700)
        
        self.__create_toolbars()
        self.__create_menu()
        self.__create_statusbar()
        # Set intro message
        self.status_label.setText("Welcome to QtSimiam")
        
        # create XML file dialog
        self._world_dialog = QtGui.QFileDialog(self,
                                "Select World File",
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
        self.__viewer = SimulatorViewer()
        scrollArea.setWidget(self.__viewer)
        scrollArea.setWidgetResizable(True)

        #self.setDockOptions(QtGui.QMainWindow.AllowNestedDocks)
        self.setDockOptions(QtGui.QMainWindow.DockOptions())

        self.__sim_timer = QtCore.QTimer(self)
        self.__sim_timer.setInterval(10)
        self.__sim_timer.timeout.connect(self.__update_time)
        
        self.__sim_queue = queue.Queue()
        
        # create the simulator thread
        self._simulator_thread = sim.Simulator(self.__viewer.renderer,
                                               self.__sim_queue)

        self.__in_queue = self._simulator_thread._out_queue
                                               
        self.__dockmanager = DockManager(self)
        self.__dockmanager.apply_request.connect(self.apply_parameters)

        self._simulator_thread.start()
        self.__sim_timer.start()
        
    def __create_toolbars(self):
        
        tbar = QtGui.QToolBar("Control",self)
        tbar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)
        
        #self.__time_label = QtGui.QLabel("00:00.0",self)
        #self.__time_label.setToolTip("Elapsed time")
        #tbar.addWidget(self.__time_label)
        
        self.revaction = \
            tbar.addAction(QtGui.QIcon("./res/image/arrow-left-double.png"),
                        "Rewind",
                        self._on_rewind)
        self.revaction.setStatusTip("Reset simulation")
        self.runaction = \
            tbar.addAction(QtGui.QIcon("./res/image/arrow-right.png"),
                           "Run",
                           self._on_run)
        self.runaction.setStatusTip("Run simulation")
        self.pauseaction = \
            tbar.addAction(QtGui.QIcon("./res/image/media-playback-pause-7.png"),
                       "Pause",
                       self._on_pause)
        self.pauseaction.setStatusTip("Pause simulation")
        
        self.revaction.setEnabled(False)
        self.runaction.setEnabled(False)
        self.pauseaction.setVisible(False)
        
        self.__speed_slider = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.__speed_slider.setToolTip("Adjust speed")
        self.__speed_slider.setStatusTip("Adjust simulation speed")
        self.__speed_slider.setTickPosition(QtGui.QSlider.NoTicks)
        self.__speed_slider.setMaximumWidth(300)
        self.__speed_slider.setRange(-100,0)
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
        a.setStatusTip("Show/hide grid")
        a.triggered[bool].connect(self._show_grid)
        a.setCheckable(True)
        a.setChecked(False)

        a = tbar.addAction(QtGui.QIcon("./res/image/robot-sensors.png"),
                           "Show/Hide sensors")
        a.setStatusTip("Show/hide robot sensors")
        a.triggered[bool].connect(self._show_sensors)
        a.setCheckable(True)
        a.setChecked(True)
        
        a = tbar.addAction(QtGui.QIcon("./res/image/robot-tracks.png"),
                           "Show/Hide robot trajectores")
        a.setStatusTip("Show/hide robot trajectores")
        a.triggered[bool].connect(self._show_tracks)
        a.setCheckable(True)
        a.setChecked(True)
        
        zoom_group = QtGui.QActionGroup(tbar)
        a = tbar.addAction(QtGui.QIcon("./res/image/zoom-scene.png"),
                           "Show all",
                            self._zoom_scene)
        a.setStatusTip("Show the whole world in view")
        a.setCheckable(True)
        a.setChecked(True)
        zoom_group.addAction(a)
        
        a = tbar.addAction(QtGui.QIcon("./res/image/zoom-robot.png"),
                           "Follow robot",
                           self._zoom_robot)
        a.setStatusTip("Center the view on robot")
        a.setCheckable(True)
        a.setChecked(False)
        zoom_group.addAction(a)

        self.act_rot_robot = \
            tbar.addAction(QtGui.QIcon("./res/image/zoom-robot-rot.png"),
                           "Follow robot orientation",
                           self._rot_robot)
        self.act_rot_robot.setStatusTip("Rotate the view with the robot")
        self.act_rot_robot.setCheckable(True)
        self.act_rot_robot.setChecked(False)
        self.act_rot_robot.setEnabled(False)

        self.__zoom_slider = QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.__zoom_slider.setTickPosition(QtGui.QSlider.NoTicks)
        self.__zoom_slider.setToolTip("Adjust zoom")
        self.__zoom_slider.setStatusTip("Zoom in/out on robot")
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
        a = file_menu.addAction(QtGui.QIcon.fromTheme("document-open"),
                                "Open XML &World",
                                self._on_open_world,
                                QtGui.QKeySequence(QtGui.QKeySequence.Open))
        a.setStatusTip("Open a new simulation")
                            
        file_menu.addSeparator()
        a = file_menu.addAction(QtGui.QIcon.fromTheme("application-exit"),
                                "E&xit",
                                self.close,
                                QtGui.QKeySequence(QtGui.QKeySequence.Quit)
                                )
        a.setToolTip("Quit the Program")
        a.setStatusTip("Exit QtSimiam")
                            
    def __create_statusbar(self):      
        self.setStatusBar(QtGui.QStatusBar())
        self.status_label = QtGui.QLabel("",self.statusBar())
        self.statusBar().addWidget(self.status_label)

    def closeEvent(self,event):
        self.__sim_timer.stop()
        self.__sim_queue.put(('stop',()))
        while self._simulator_thread.isAlive():
            self.process_events(True)
            self._simulator_thread.join(0.1)
        super(SimulationWidget,self).closeEvent(event)

    def make_param_window(self,robot_id,name,parameters):       
        # FIXME adding to the right for no reason
        self.__dockmanager.add_dock_right(robot_id, name, parameters)

    def load_world(self,filename):
        if not os.path.exists(filename):
            filename = os.path.join('worlds',filename)
            if not os.path.exists(filename):
                print "Cannot open file {}".format(filename)
                return
        self.__dockmanager.clear()
        #self.revaction.setEnabled(False)
        #self.runaction.setEnabled(True)
        self.__sim_queue.put(('read_config',(filename,)))

    # Slots
    @QtCore.pyqtSlot()
    def _on_rewind(self): # Start from the beginning

        self.pauseaction.setVisible(False)
        self.runaction.setVisible(True)

        self.pauseaction.setEnabled(False)
        self.revaction.setEnabled(False)

        self.__speed_slider.setEnabled(False)
        #self.__time_label.setText("00:00.0")
        self.__sim_queue.put(('reset_simulation',()))

    @QtCore.pyqtSlot()
    def _on_run(self): # Run/unpause
        self.pauseaction.setVisible(True)
        self.runaction.setVisible(False)
        self.runaction.setEnabled(False)
        self.__sim_queue.put(('start_simulation',()))

    @QtCore.pyqtSlot()
    def _on_pause(self): # Pause
        self.pauseaction.setVisible(False)
        self.runaction.setVisible(True)
        
        self.pauseaction.setEnabled(False)
        self.__speed_slider.setEnabled(False)
        
        self.__sim_queue.put(('pause_simulation',()))

    @QtCore.pyqtSlot()
    def _on_open_world(self):
        self._on_pause()
        if self._world_dialog.exec_():
            self.load_world(self._world_dialog.selectedFiles()[0])
            
    @QtCore.pyqtSlot(bool)
    def _show_grid(self,show):
        self.__sim_queue.put(('show_grid',(show,)))

    @QtCore.pyqtSlot(bool)
    def _show_sensors(self,show):
        self.__sim_queue.put(('show_sensors',(show,)))
            
    @QtCore.pyqtSlot(bool)
    def _show_tracks(self,show):
        self.__sim_queue.put(('show_tracks',(show,)))
            
    @QtCore.pyqtSlot()
    def _zoom_scene(self):
        self.__zoom_slider.setEnabled(False)
        self.act_rot_robot.setEnabled(False)
        self.__sim_queue.put(('focus_on_world',()))

    @QtCore.pyqtSlot()
    def _zoom_robot(self):
        self.__zoom_slider.setEnabled(True)
        self.act_rot_robot.setEnabled(True)
        self.__sim_queue.put(('focus_on_robot',(self.act_rot_robot.isChecked(),)))
        self.__sim_queue.put(('adjust_zoom',(5.0**(self.__zoom_slider.value()/100.0),)))

    @QtCore.pyqtSlot()
    def _rot_robot(self):
        self.__sim_queue.put(('focus_on_robot',(self.act_rot_robot.isChecked(),)))
            
    @QtCore.pyqtSlot(int)
    def _scale_zoom(self,value):
        zoom = 5.0**(value/100.0)
        self.__sim_queue.put(('adjust_zoom',(zoom,)))
        self.__zoom_label.setText(" Zoom: %.1fx"%(zoom))

    @QtCore.pyqtSlot(int)
    def _scale_time(self,value):
        m = 10.0**((value-self.__zoom_factor)/100.0)
        self.__sim_queue.put(('set_time_multiplier',(m,)))
        self.__speed_label.setText(" Speed: %.1fx"%m)

    @QtCore.pyqtSlot()
    def __update_time(self):
        if self._simulator_thread.is_running():
            t = self._simulator_thread.get_time()
            minutes = int(t//60)
            #self.__time_label.setText("%02d:%04.1f"%(minutes,t - minutes*60))
            self.status_label.setText(
                "Simulation running... {:02d}:{:04.1f}".format(minutes,t - minutes*60))
        self.process_events(True)
    
    def process_events(self, process_all = False):
        while not self.__in_queue.empty():
            tpl = self.__in_queue.get()
            if isinstance(tpl,tuple) and len(tpl) == 2:
                name, args = tpl
                if name in self.__class__.__dict__:
                    try:
                        self.__class__.__dict__[name](self,*args)
                    except TypeError:
                        print "Wrong UI event parameters {}{}".format(name,args)
                        raise
                else:
                    print "Unknown UI event '{}'".format(name)
            else:
                print "Wrong UI event format '{}'".format(tpl)
            self.__in_queue.task_done()
            if not process_all:
                return
    
    def apply_parameters(self, robot_id, params):
        self.__sim_queue.put(('apply_parameters', (robot_id, params)))
            
### Queue processing
        
    def simulator_running(self):
        self.pauseaction.setVisible(True)
        self.runaction.setVisible(False)
        self.runaction.setEnabled(False)
        self.revaction.setEnabled(True)
        self.pauseaction.setEnabled(True)
        self.__speed_slider.setEnabled(True)
    
    def simulator_paused(self):
        self.pauseaction.setVisible(False)
        self.runaction.setVisible(True)
        
        self.pauseaction.setEnabled(False)
        self.__speed_slider.setEnabled(False)

        self.runaction.setEnabled(True)
        #self.revaction.setEnabled(True)
        t = self._simulator_thread.get_time()
        minutes = int(t//60)
        #self.__time_label.setText("%02d:%04.1f"%(minutes,t - minutes*60))
        self.status_label.setText(
            "Simulation paused... {:02d}:{:04.1f}".format(minutes,t - minutes*60))

    def simulator_reset(self):
        self.pauseaction.setVisible(False)
        self.runaction.setVisible(True)

        self.pauseaction.setEnabled(False)
        self.revaction.setEnabled(False)

        self.runaction.setEnabled(True)
        self.status_label.setText("Simulation ready")

    def simulator_stopped(self):
        # FIXME this function isn't necessary
        #self.__sim_timer.stop()
        self.runaction.setEnabled(False)
        self.pauseaction.setEnabled(False)
        self.revaction.setEnabled(False)
        self.__speed_slider.setEnabled(False)
        
    def update_view(self):
        self.__viewer.update_bitmap()
        
    def simulator_exception(self,e_type, e_value, e_traceback):
        QtGui.QMessageBox.critical(self,"{}: {}".format(e_type.__name__,e_value),"\n".join(format_exception(e_type,e_value,e_traceback)))
            
#end QtSimiamFrame class

class SimulatorViewer(QtGui.QFrame):
    def __init__(self, parent = None):
        super(SimulatorViewer, self).__init__(parent)
        self.__bitmap = QtGui.QPixmap()
        self.__blt_bitmap = QtGui.QImage(self.size(), QtGui.QImage.Format_ARGB32)
        self.renderer = QtRenderer(self.__blt_bitmap)
        self.__resize_on_paint = False
        # code for async calling of update
        self.update_ = self.metaObject().method(self.metaObject().indexOfMethod('update()'))

    def paintEvent(self, event):
        super(SimulatorViewer, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(),QtCore.Qt.white)
        s = self.__bitmap.rect().size()
        s.scale(self.rect().size(),QtCore.Qt.KeepAspectRatio)
        dx = (self.width() - s.width())/2
        dy = (self.height() - s.height())/2
        painter.drawPixmap(QtCore.QRect(QtCore.QPoint(dx,dy),s),self.__bitmap,self.__bitmap.rect())
        
    def update_bitmap(self):
        self.__bitmap = QtGui.QPixmap.fromImage(self.__blt_bitmap)
        # resize the canvas - at this point nothing is being drawn
        if self.__resize_on_paint:
            self.__blt_bitmap = QtGui.QImage(self.width(),
                                            self.height(),
                                            QtGui.QImage.Format_ARGB32)
            self.renderer.set_canvas(self.__blt_bitmap)          
            self.__resize_on_paint = False
        self.update()

    def resizeEvent(self,event):
        """Resize panel and canvas"""
        # use cached size and flag
        self.__resize_on_paint = True

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            simWidget.load_world(sys.argv[1])
        else:
            print "Too many command-line options"
    app.exec_()
