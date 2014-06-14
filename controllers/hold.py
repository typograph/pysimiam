#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from core.controller import Controller
import math
import numpy

class Hold(Controller):
    """This controller halts the robot"""
    def __init__(self):
        Controller.__init__(self)

    def set_parameters(self,params):
        """This controller has no parameters"""
        pass

    def execute(self,state,dt):
        """Stop the robot"""
        return [0.,0.]
