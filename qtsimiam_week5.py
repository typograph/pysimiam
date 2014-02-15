#!/usr/bin/env python
# QtSimiam for Coursera Week 5
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
from __future__ import print_function
import sys
sys.path.insert(0, './scripts')
sys.path.insert(0, './gui')
from PyQt4 import QtGui

from coursera import Week5
from qt_mainwindow import SimulationWidget

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
