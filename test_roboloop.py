#!/usr/bin/env python
# QtSimiam main executable
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
#from __future__ import print_function
import sys
sys.path.insert(0, './scripts')
sys.path.insert(0, './gui')
from PyQt4 import QtGui
from time import sleep

from qt_mainwindow import SimulationWidget

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    simWidget.load_world("test_realtime_bot.xml")
    simWidget.run_simulation()
    app.exec_()
