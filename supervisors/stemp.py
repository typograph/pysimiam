"""PySimiam
Author: John Alexander
ChangeDate: 4 FEB 2013; 1300EST
Description: This is a template for the user-defined Supervisor
"""
from scripts.supervisor import Supervisor
import controllers

class Stemp(Supervisor):
    '''
    This is a template for the user-defined class, the criteria method reads the ir sensors (or other available information) from the robot and makes a decision as to which controller to use
    '''
    def evalcriteria(self):
        #Modify Below Here
		
        self.current = 'gotogoal'
		
        #Modify Above Here