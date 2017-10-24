#!/usr/bin/env python
# QtSimiam for Coursera Week 5
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
import sys

from gui.qt.Qt import QtGui
from gui.qt.mainwindow import SimulationWidget
from core.coursera import Week5

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.setTestSuite(Week5)
    simWidget.superv_action.trigger()
    simWidget.show()
    if len(sys.argv) > 1:
        simWidget.load_world("week5_{}.xml".format(sys.argv[1]))
    else:
        simWidget.load_world("week5_blending.xml")
    app.exec_()
