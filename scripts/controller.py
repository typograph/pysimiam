"""PySimiam
Author: John Alexander
ChangeDate: 4 FEB 2013; 1300EST
Description: This is the Supervisor class for PySimiam.
"""
import math

class Controller():
    def execute(self,supervisor,estimatedPose):
        self.readInstruments(supervisor)
        self.EstimatedPose=supervisor.EstimatedPose
        wheelspeeds=self.algorithm()
        return wheelspeeds

    def readInstruments(self,parent):
        self.IR_Sensors=supervisor.robot.ir_sensors
        self.ticks=supervisor.robot
