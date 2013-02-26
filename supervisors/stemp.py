"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is a template for the user-defined Supervisor
"""
from supervisor import Supervisor

class Stemp(Supervisor):
    '''
    This is a template for the user-defined class, the criteria
    method reads the ir sensors (or other available information)
    from the robot and makes a decision as to which controller to use
    '''
    def eval_criteria(self):
        #Modify Below Here
        
        self.current = self.controllers['gotogoal']
        
        #Modify Above Here
