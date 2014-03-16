#
# (c) PySimiam Team 2014
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# The Qt interface for PC-controlled real robots
#

import sys
import os
import socket

from .Qt import QtGui, QtCore

from core.ui import uiParameter, uiInt, uiFloat, uiBool, uiSelect, uiGroup

from .paramwindow import ParamWidget
from .courseradock import CourseraDock
from .logdock import LogDock

class PlayPauseAction(QtGui.QAction):
    def __init__(self, parent, run_slot, pause_slot):
        QtGui.QAction.__init__(self, parent)
        self.playset = (QtGui.QIcon.fromTheme("media-playback-start",
                            QtGui.QIcon("./res/image/arrow-right.png")),
                        "Run",
                        run_slot,
                        "Run simulation")
        self.pauseset = (QtGui.QIcon.fromTheme("media-playback-pause",
                            QtGui.QIcon("./res/image/media-playback-pause-7.png")),
                         "Pause",
                         pause_slot,
                         "Pause simulation")
        self.triggered.connect(self.__on_click)
        self.reset()
        
    def __on_click(self):
        self.callback()
        self.set_state()

    def reset(self):
        self.click_to_run = False
        self.set_state(self.playset)
        
    def set_state(self, actset = None):
        if actset is None:
            if self.click_to_run:
                actset = self.pauseset
            else:
                actset = self.playset
        self.click_to_run = not self.click_to_run
        self.setIcon(actset[0])
        self.setText(actset[1])
        self.callback = actset[2]
        self.setStatusTip(actset[3])

class ControlWidget(QtGui.QWidget):
    connected = QtCore.Signal()
    
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self,parent)
        
        vlayout = QtGui.QVBoxLayout(self)
        
        hlayout = QtGui.QHBoxLayout()
        vlayout.addLayout(hlayout)
        
        self.ipWidget = QtGui.QLineEdit(self)
        self.ipWidget.setText("127.0.0.1")
        self.ipWidget.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"{0}\.{0}\.{0}\.{0}".format(r"(\d|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])"))))
        
        hlayout.addWidget(self.ipWidget)
        
        self.portWidget = QtGui.QSpinBox(self)
        self.portWidget.setRange(0,65536)
        self.portWidget.setValue(5005)
        
        hlayout.addWidget(self.portWidget)
        
        self.cnctButton = QtGui.QPushButton("Connect",self)
        self.cnctButton.clicked.connect(self.connect2bot)
        
        hlayout.addWidget(self.cnctButton)
 
        vlayout.addStretch(1)
        
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        
    def connect2bot(self):
        try:
            ui = self.getReply("UI?")
            self.paramWidget = ParamWidget(self, 0, eval(ui,{
                'uiInt':uiInt,
                'uiFloat':uiFloat,
                'uiBool':uiBool,
                'uiSelect':uiSelect,
                'uiGroup':uiGroup}))
            self.paramWidget.apply_request.connect(self.apply_params)
#            self.layout().removeItem(self.layout().itemAt(1))
#            self.layout().addWidget(self.paramWidget)
            self.layout().insertWidget(1,self.paramWidget)
            self.cnctButton.setEnabled(False)
            self.ipWidget.setEnabled(False)
            self.portWidget.setEnabled(False)
            self.connected.emit()
        except IOError as e:
            print(e)
            
    def apply_params(self, robot_id, params):
        try:
            self.sendCmd("PARAM={}".format(repr(params)))
        except IOError as e:
            print(e)
            
    def run(self):
        try:
            self.sendCmd("RUN")
        except IOError as e:
            print(e)

    def pause(self):
        try:
            self.sendCmd("PAUSE")
        except IOError as e:
            print(e)

    def getReply(self,command):
        uirequest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        uirequest.connect((self.ipWidget.text(), self.portWidget.value()))
        if sys.version_info[0] == 3:
            command = command.encode("utf-8")
        uirequest.send(command)
        uirequest.shutdown(socket.SHUT_WR)
        reply = ""
        while True:
            cbuffer = uirequest.recv(1024)
            if not cbuffer:
                break
            reply += cbuffer.decode("utf-8")
        uirequest.close()
        print(reply)
        return reply

    def sendCmd(self,command):
        uirequest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        uirequest.connect((self.ipWidget.text(), self.portWidget.value()))
        if sys.version_info[0] == 3:
            command = command.encode("utf-8")
        uirequest.send(command)
        uirequest.shutdown(socket.SHUT_RDWR)
        uirequest.close()
        

class SimulationWidget(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setWindowTitle("QtSimiam - Remote control")
        self.setWindowIcon(QtGui.QIcon("./res/image/appicon.png"))
        self.resize(300,700)

        self.control = ControlWidget(self)
        self.setCentralWidget(self.control)
        
        self.create_actions()
        self.create_toolbars()
        self.create_menu()
        self.create_statusbar()
        # Set intro message
        self.status_label.setText("Welcome to QtSimiam")        

    def create_actions(self):
        
        self.exit_action = \
            QtGui.QAction(QtGui.QIcon.fromTheme("application-exit"),
                    "E&xit",
                    self)
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut(QtGui.QKeySequence(QtGui.QKeySequence.Quit))
        self.exit_action.setToolTip("Quit the Program")
        self.exit_action.setStatusTip("Exit QtSimiam")
        
        self.run_action = PlayPauseAction(self, self.control.run, self.control.pause)
        self.run_action.setEnabled(False)              
        self.control.connected.connect(lambda: self.run_action.setEnabled(True))

        self.about_action = \
            QtGui.QAction(QtGui.QIcon.fromTheme("help-about",
                            self.windowIcon()),
                          "About",self)
        self.about_action.setStatusTip("About QtSimiam")
        self.about_action.triggered.connect(self.about)
        
    def create_toolbars(self):
        
        self.simulator_toolbar = QtGui.QToolBar("Control",self)
        self.simulator_toolbar.setAllowedAreas(QtCore.Qt.TopToolBarArea | QtCore.Qt.BottomToolBarArea)
        
        self.simulator_toolbar.addAction(self.run_action)
                              
        self.addToolBar(self.simulator_toolbar)

    def create_menu(self):
        menu = QtGui.QMenuBar(self)
        self.setMenuBar(menu)
        
        file_menu = menu.addMenu("&File")
        
        file_menu.addAction(self.exit_action)
        
        run_menu = menu.addMenu("&Control")
        
        run_menu.addAction(self.run_action)
        
        self.run_menu = run_menu
        
        help_menu = menu.addMenu("&Help")
        help_menu.addAction(self.about_action)
        
    def create_statusbar(self):      
        self.setStatusBar(QtGui.QStatusBar())
        self.status_label = QtGui.QLabel("",self.statusBar())
        self.status_label.setFrameShape(QtGui.QFrame.NoFrame)
        self.statusBar().addWidget(self.status_label)

    # Slots
    def about(self):
        QtGui.QMessageBox.about(self,"About QtSimiam",
        """<b>PySimiam (Qt)</b><br>
        Robot simulator<br>
        &copy; Pysimiam Team
        """)

