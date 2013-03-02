#!/usr/bin/python
#QtSimiam
#Author: Tim Fuchs
#Description: This is the top-level application for QtSimiam.
import sys
sys.path.insert(0, './scripts')
from PyQt4.QtGui import QApplication
from qt_mainwindow import SimulationWidget
from qt_plotwindow import use_matplotlib_backend

if __name__ == "__main__":
    app = QApplication(sys.argv)
    use_matplotlib_backend()
    simWidget = SimulationWidget()
    simWidget.show()
    simWidget.load_world("week2.xml")
    simWidget.add_graph([
            [("Robot X", "robot.get_pose().x", 'red'),
             ("Goal X", "supervisor.ui_params.goal.x",'blue')],
            [("Robot Y", "robot.get_pose().y", 'red'),
             ("Goal X", "supervisor.ui_params.goal.y",'blue')],
            [("Robot Theta", "robot.get_pose().theta", 'red'),
             ("Angle to goal","math.atan2(supervisor.ui_params.goal.y - robot.get_pose().y,supervisor.ui_params.goal.x - robot.get_pose().x)", 'blue')]
            ])
    app.exec_()
