#!/usr/bin/env python
# QtSimiam for Coursera Week 4
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
from __future__ import print_function
import sys
sys.path.insert(0, './scripts')
sys.path.insert(0, './gui')
from PyQt4 import QtGui

from qt_mainwindow import SimulationWidget
from coursera import Week4

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.superv_action.trigger()
    simWidget.setTestSuite(Week4)
    simWidget.show()
    simWidget.load_world("week4.xml")
    app.exec_()
