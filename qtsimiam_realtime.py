#!/usr/bin/env python
# QtSimiam main executable
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam for controlling real robots.
import sys

from qui.qt.Qt import QtGui
from gui.qt.pcmain import SimulationWidget

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    simWidget.load_world("qb_realtime_pc.xml")
    app.exec_()

