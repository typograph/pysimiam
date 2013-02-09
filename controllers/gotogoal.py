"""PySimiam
Author: John Alexander
ChangeDate: 4 FEB 2013; 1300EST
Description: This is the Supervisor class for PySimiam.
"""
from scripts.controller import Controller

class Gotogoal(Controller):
    '''
    This is a template for the user-defined class, the criteria method reads the ir sensors (or other available information) from the robot and makes a decision as to which controller to use
    '''
    def algorithm(self,goalPose,EstimatedPose):
        #Modify Below Here
        theta=EstimatedPose().theta
        
        #Modify Above Here
        return wheelspeeds