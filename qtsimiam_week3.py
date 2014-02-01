#!/usr/bin/python2
# QtSimiam
# Author: Tim Fuchs
# Description: This is the top-level application for QtSimiam.
from __future__ import print_function
import sys
sys.path.insert(0, './scripts')
sys.path.insert(0, './gui')
from PyQt4 import QtGui

from qt_mainwindow import SimulationWidget
from coursera import Week3

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.superv_action.trigger()
    simWidget.setTestSuite(Week3)
    simWidget.show()
    simWidget.load_world("week3.xml")
    simWidget.add_graph([
            [("Robot X", "robot.get_pose().x", 'red'),
             ("Goal X", "supervisor.parameters.goal.x",'blue')],
            [("Robot Y", "robot.get_pose().y", 'red'),
             ("Goal X", "supervisor.parameters.goal.y",'blue')],
            [("Robot Theta", "robot.get_pose().theta", 'red'),
             ("Angle to goal","math.atan2(supervisor.parameters.goal.y - robot.get_pose().y,supervisor.parameters.goal.x - robot.get_pose().x)", 'blue')]
            ])
    app.exec_()
