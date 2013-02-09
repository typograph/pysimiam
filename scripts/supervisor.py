"""PySimiam
Author: John Alexander
ChangeDate: 4 FEB 2013; 1300EST
Description: This is the Supervisor class for PySimiam.
"""
import controllers
from string import capitalize

class Supervisor:
    '''
    I'm sure this is a sloppy way of instantiating these classes I couldn't
	come up with anything cleaner
    '''
    def __init__(self,robot,cntrlList):
        self.attachRobot(robot)
        for module in cntrlList:
            __import__('controllers.'+module)
        self.buildDict(cntrlList)
        self.EstimatedPose=self.robot.get_pose

    def attachRobot(self,robot):
        self.robot=robot

    def setCurrent(self, cntrl):
        self.current=cntrl

    def getCurrent(self):
        return self.current

    def buildDict(self,cntrlList):
        self.controllers={}
        for controller in cntrlList:
            temp=getattr(controllers,controller)
            temp2=getattr(temp, capitalize(controller[0])+controller[1:])
            self.controllers[controller]=temp2()

    def execute(self):
        self.evalcriteria(self) #User defined algorithm which selects the controller to use for this time step

        wheel_speeds=self.controllers[self.current].execute()
        self.robot.set_wheel_speeds=wheel_speeds