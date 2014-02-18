#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controller import Controller
import math
import numpy

import pygame
from pygame import joystick

class JoystickController(Controller):
    """The joystick controller steers the robot according to the joystick input."""
    def __init__(self, params):
        '''Initialize internal variables'''
        
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

        self.v_max = params[1]
        self.w_max = params[2]

        Controller.__init__(self, params[0])


    def joystick_count(self):
        return joystick.get_count()

    def set_parameters(self, params):
        """Set joystick and its axes"""
        
        if self.i_j != params.i_j and \
           params.i_j < joystick.get_count() and \
           params.i_j >= 0:
            self.i_j = params.i_j
            self.joystick.quit()
            self.joystick = joystick.Joystick(self.i_j)
            self.joystick.init()
            
        if self.i_x != params.i_x and \
           params.i_x < self.joystick.get_numaxes() and \
           params.i_x >= 0:
            self.i_x = params.i_x
            
        if self.i_y != params.i_y and \
           params.i_y < self.joystick.get_numaxes() and \
           params.i_y >= 0 and \
           params.i_y != self.i_x:
            self.i_y = params.i_y
            
        if self.i_x == self.i_y:
            if self.i_x + 1 >= self.joystick.get_numaxes():
                self.i_y = self.i_x - 1
            else:
                self.i_y = self.i_x + 1
                
        self.inv_x = params.inv_x
        self.inv_y = params.inv_y

    def get_heading(self, state):
        """Get the direction in which the controller wants to move the robot
        as a vector in the robot's frame of reference.
        
        :return: a numpy array [x, y, z] with z = 1.
        """
        raise NotImplementedError("PIDController.get_heading")
    
    def get_heading_angle(self, state):
        """Return the heading as an angle in the robot's frame of reference."""

        # The vector to follow
        heading = self.get_heading(state)

        return math.atan2(heading[1],heading[0])
    
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
