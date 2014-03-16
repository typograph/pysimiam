#!/usr/bin/env python
# QtSimiam for Coursera Week 4
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
import sys

from qui.qt.Qt import QtGui
from gui.qt.mainwindow import SimulationWidget
from core.coursera import Week4

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.superv_action.trigger()
    simWidget.setTestSuite(Week4)
    simWidget.show()
    simWidget.load_world("week4.xml")
    app.exec_()
