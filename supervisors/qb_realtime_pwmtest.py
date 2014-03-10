#
# (c) PySimiam Team 2014
#
# Contact person: John Witten <jon.witten@gmail.com>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisor import Supervisor
from helpers import Struct
from pose import Pose
from ui import uiInt

class PWMTest(Supervisor):
    """The PWMTest is here to test your robot's PWM values."""
    def __init__(self, robot_pose, robot_info, options = None):
        """Initialize internal variables"""
        Supervisor.__init__(self, robot_pose, robot_info)

        # initialize memory registers
        self.left_ticks  = robot_info.wheels.left_ticks
        self.right_ticks = robot_info.wheels.right_ticks
        
    def init_default_parameters(self):
        """Sets the default PID parameters, goal, and velocity"""
        self.parameters = Struct({'left':0, 'right':0})
        
    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
        if p is None:
            p = self.parameters
        
        return [(('left','Left Wheel PWM'), uiInt(p.left)),
					 (('right','Right Wheel PWM'), uiInt(p.right))]

    def set_parameters(self,params):
        """Set param structure from docker"""
        self.parameters.left = params.left
        self.parameters.right = params.right
                                     
    def execute(self, robot_info, dt):
        """Inherit default supervisor procedures and return unicycle model output (x, y, theta)"""
        dl = abs(robot_info.wheels.left_ticks - self.left_ticks) + abs(robot_info.wheels.right_ticks - self.right_ticks)
        self.left_ticks = robot_info.wheels.left_ticks
        self.right_ticks = robot_info.wheels.right_ticks
        if dl > 0:
            self.log("Encoders: {} L , {} R".format(self.left_ticks,self.right_ticks))
        return self.parameters.left, self.parameters.right

