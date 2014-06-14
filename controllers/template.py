import math
import numpy

from core.controller import Controller

class Template(Controller):
    """Template controller with required functions"""
    def __init__(self, o1, o2):
        Controller.__init__(self)
        self.o1 = o1
        self.o2 = o2

    def set_parameters(self, p1, p2, p3):
        """Set PID values
        
        """
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def execute(self, state, dt):
        """Required function: must return a unicycle model

        return --> unicycle model list [velocity, omega]"""

        v_ = 0 #some default value
        w_ = 0 #another default value

        return [v_, w_]
