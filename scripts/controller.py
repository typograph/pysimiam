"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is the Controller class for PySimiam.
"""
import math
from xmlparser import XMLParser

class Controller():
    def __init__(self,params):
        """Initialize the controller with parameters"""
        self.set_parameters(params)
    
    def execute(self, state, dt):
        """Given state and elapsed time, calculate and return robot motion parameters
        
        To be implemented in subclasses
        """
        raise NotImplementedError("Controller.execute")

    def set_parameters(self,params):
        """Get the internal paramters from the params structure
        
        To be implemented in subclasses
        """
        raise NotImplementedError("Controller.set_parameters")
    