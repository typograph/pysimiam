#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class Hold(Controller):
    """This controller halts the robot"""
    def __init__(self, params):
        Controller.__init__(self,params)

    def set_parameters(self,params):
        """This controller has no parameters"""
        pass

    def execute(self,state,dt):
        """Stop the robot"""
        return [0.,0.]
