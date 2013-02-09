"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is the Supervisor class for PySimiam.
"""

from string import capitalize

class Supervisor:
    def __init__(self,robot,cntrl_list):
        self.attach_robot(robot)
        self.controller_modules={}
        for module_name in cntrl_list:
            self.controller_modules[module_name]=__import__(module_name)

        self.build_dict(cntrl_list)
        self.pose_est=self.robot.get_pose #define the starting pose

    def attach_robot(self,robot):
        self.robot=robot

    def set_current(self, cntrl):
        self.current=self.controllers[cntrl]

    def get_current(self):
        return self.current

    def build_dict(self,cntrl_list):
        self.controllers={}
        for controller in cntrl_list:
            class_name=getattr(self.controller_modules[controller], capitalize(controller[0])+controller[1:])
            self.controllers[controller]=class_name()

    def execute(self,dt):
        self.eval_criteria() #User-defined algorithm
        output=self.current.execute(self,dt)#execute the current class
        self.pose_est=[0,0,0]
