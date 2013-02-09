"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is the Controller class for PySimiam.
"""
import math

class Controller():
    def execute(self,supervisor,dt):
        self.read_instruments(supervisor)
        self.pose_est=supervisor.pose_est
        output=self.algorithm(self.pose_est,dt)
        return output

    def read_instruments(self,supervisor):
        self.ir_sensors=supervisor.robot.ir_sensors
        self.ticks=supervisor.robot
