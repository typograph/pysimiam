#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from math import sqrt, sin, cos, atan2

from core.simobject import Path
from core.supervisor import Supervisor
from core.pose import Pose
from core.helpers import Struct
from core.ui import uiInt, uiBool

from supervisors.quickbot import QuickBotSupervisor


class QBJoystickSupervisor(QuickBotSupervisor):
    """Control the robot with a joystick!!!

       The supervisor will choose two first axes, and assign one to
       v and one to w control.
    """
    def __init__(self, robot_pose, robot_color, robot_info, options=None):
        """Create the controller"""

        QuickBotSupervisor.__init__(self, robot_pose, robot_color, robot_info)

        v_max = robot_info.wheels.max_velocity*robot_info.wheels.radius
        w_max = v_max/robot_info.wheels.base_length

        self.jcontroller = self.create_controller(
            'joystick.JoystickController',
            v_max, w_max)

        self.current = self.jcontroller

        self.joystick = Struct()
        self.joystick.i_j = self.jcontroller.i_j  # Index of the joystick
        self.joystick.i_x = self.jcontroller.i_x  # Index of the X axis
        self.joystick.inv_x = self.jcontroller.inv_x    # Invert X axis
        self.joystick.i_y = self.jcontroller.i_y  # Index of the Y axis
        self.joystick.inx_y = self.jcontroller.inv_y    # Invert Y axis
        
    def set_parameters(self, params):
        """Set parameters for itself and the controllers"""
        self.joystick = params.joystick
        self.jcontroller.set_parameters(self.joystick.i_j,
                                        self.joystick.i_x,
                                        self.joystick.i_y,
                                        self.joystick.inv_x,
                                        self.joystick.inv_y)

    def get_parameters(self):
        return Struct({"joystick": self.joystick})

    def get_controller_state(self):
        return None  # The joystick doesn't need this state.

    def get_ui_description(self):
        """Returns the UI description for the docker"""

        return [('joystick', [
                (('i_j', "Joystick index"),
                    uiInt(self.joystick.i_j,
                          0, self.jcontroller.joystick_count()-1)),
                (('i_x', "Omega axis"),
                    uiInt(self.joystick.i_x, 0, 100)),
                (('inv_x', "Invert axis"),
                    uiBool(self.joystick.inv_x)),
                (('i_y', "Velocity axis"),
                    uiInt(self.joystick.i_y, 0, 100)),
                (('inv_y', "Invert axis"),
                    uiBool(self.joystick.inv_y))])]

    def draw_background(self, renderer):
        pass

    def draw_foreground(self, renderer):
        pass
