#!/usr/bin/python
#QtSimiam
#Author: Tim Fuchs
#Description: This is the top-level application for QtSimiam.
import sys
sys.path.insert(0, './scripts')
from PyQt4.QtGui import QApplication
from qt_mainwindow import SimulationWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    simWidget = SimulationWidget()
    simWidget.show()
    simWidget.load_world("week2.xml")
    simWidget.add_graph([
            [("Robot X", "robot.get_pose().x", (1.,0,0)),
             ("Goal X", "supervisor.ui_params.goal.x",(0,0,1.0))],
            [("Robot Y", "robot.get_pose().y", (1.,0,0)),
             ("Goal X", "supervisor.ui_params.goal.y",(0,0,1.0))],
            [("Robot Theta", "robot.get_pose().theta", (1.,0,0)),
             ("Angle to goal","math.atan2(supervisor.ui_params.goal.y - robot.get_pose().y,supervisor.ui_params.goal.x - robot.get_pose().x)", (0,0,1.0))]
            ])
    app.exec_()
