#!/usr/bin/env python
# QtSimiam for Coursera Week 7
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
from __future__ import print_function
import sys
from PyQt4 import QtGui

from gui.qt_mainwindow import SimulationWidget
from core.coursera import Week7

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.superv_action.trigger()
    simWidget.show()
    simWidget.setTestSuite(Week7)
    simWidget.load_world("week7.xml")
    app.exec_()
