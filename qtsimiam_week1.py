#!/usr/bin/env python
# QtSimiam for Coursera Week 1
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
import sys

from gui.qt.Qt import QtGui
from gui.qt.mainwindow import SimulationWidget
from core.coursera import Week1

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.setTestSuite(Week1)
    simWidget.show()
    simWidget.load_world("week1.xml")
    app.exec_()
