#!/usr/bin/env python
# QtSimiam for Coursera Week 6
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
from __future__ import print_function
import sys
sys.path.insert(0, './scripts')
sys.path.insert(0, './gui')
from PyQt4 import QtGui

from coursera import Week6
from qt_mainwindow import SimulationWidget

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.setTestSuite(Week6)
    simWidget.superv_action.trigger()
    simWidget.show()
    simWidget.load_world("week6.xml")
    simWidget.step_action.trigger()
    app.exec_()
