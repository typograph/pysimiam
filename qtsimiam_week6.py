#!/usr/bin/env python
# QtSimiam for Coursera Week 6
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
import sys

from qui.qt.Qt import QtGui
from gui.qt.mainwindow import SimulationWidget
from core.coursera import Week6

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.setTestSuite(Week6)
    simWidget.superv_action.trigger()
    simWidget.show()
    simWidget.load_world("week6.xml")
    simWidget.step_action.trigger()
    app.exec_()
