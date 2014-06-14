#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

import math
import numpy

import pygame
from pygame import joystick

from core.controller import Controller

class JoystickController(Controller):
    """The joystick controller steers the robot according to the joystick
       input."""
    def __init__(self, v_max, w_max):
        '''Initialize internal variables'''
        Controller.__init__(self)

        # Find us a joystick

        pygame.init()
        joystick.init()

        if joystick.get_count() == 0:
            raise OSError("No joysticks found!")

        self.joystick = joystick.Joystick(0)
        self.joystick.init()
        self.i_j = 0
        self.i_x = 0
        self.i_y = 1
        self.inv_x = True
        self.inv_y = True

        self.v_max = v_max
        self.w_max = w_max

    def joystick_count(self):
        return joystick.get_count()

    def set_parameters(self, i_j, i_x, i_y, inv_x, inv_y):
        """Set joystick and its axes"""

        if self.i_j != i_j and \
           i_j < joystick.get_count() and \
           i_j >= 0:
            self.i_j = i_j
            self.joystick.quit()
            self.joystick = joystick.Joystick(self.i_j)
            self.joystick.init()

        if self.i_x != i_x and \
           i_x < self.joystick.get_numaxes() and \
           i_x >= 0:
            self.i_x = i_x

        if self.i_y != i_y and \
           i_y < self.joystick.get_numaxes() and \
           i_y >= 0 and \
           i_y != self.i_x:
            self.i_y = i_y

        if self.i_x == self.i_y:
            if self.i_x + 1 >= self.joystick.get_numaxes():
                self.i_y = self.i_x - 1
            else:
                self.i_y = self.i_x + 1

        self.inv_x = inv_x
        self.inv_y = inv_y

    def execute(self, state, dt):
        """Calculate errors and steer the robot"""

        pygame.event.pump()

        x = self.joystick.get_axis(self.i_x)
        if self.inv_x:
            x *= -1
        y = self.joystick.get_axis(self.i_y)
        if self.inv_y:
            y *= -1

        return y*self.v_max, x*self.w_max
