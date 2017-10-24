#!/usr/bin/env python
# QtSimiam for Coursera Week 3
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam.
import sys

from gui.qt.Qt import QtGui
from gui.qt.mainwindow import SimulationWidget
from core.coursera import Week3

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.superv_action.trigger()
    simWidget.setTestSuite(Week3)
    simWidget.show()
    simWidget.load_world("week3.xml")
    simWidget.add_graph([
            [("Robot theta", "robot.get_pose().theta", 'red'),
             ("Angle to goal","math.atan2(supervisor.parameters.goal.y - robot.get_pose().y,supervisor.parameters.goal.x - robot.get_pose().x)", 'blue')]
            ])
    app.exec_()
