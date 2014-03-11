"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is a template for the controller class for PySimiam.
"""
import math
import numpy

from .controller import Controller

class Ctemp(Controller):
    def __init__(self):
        self.kp=10
        self.ki=0
        self.kd=0
        '''
        Error Terms:
        self.E_k = 0
        self.e_k_1 = 0
        '''

    def algorithm(self,pose_est):
        #Modify Below Here
        
        #Modify Above Here
        return wheelspeeds
