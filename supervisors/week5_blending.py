#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.quickbot import QuickBotSupervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class QBBlendingSupervisor(QuickBotSupervisor):
    """QBlending supervisor uses a blending controller to make the robot reach the goal smoothly and without colliding wth walls."""
    def __init__(self, robot_pose, robot_info):
        """Create the controller"""
        QuickBotSupervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]
        
        # Create the controller
        self.blending = self.create_controller('week5.Blending', self.parameters)

        # Set the controller
        self.current = self.blending

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        QuickBotSupervisor.set_parameters(self,params)
        self.blending.set_parameters(self.parameters)

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        QuickBotSupervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est

        # Sensor readings in world units
        self.parameters.sensor_distances = self.get_ir_distances()
    
    def draw_foreground(self, renderer):
        """Draw controller info"""
        QuickBotSupervisor.draw_foreground(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
        # Draw arrow to goal
        renderer.set_pen(0xCC00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.goal_angle),
            arrow_length*sin(self.blending.goal_angle))

        # Draw arrow away from obstacles
        renderer.set_pen(0xCCFF0000)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.away_angle),
            arrow_length*sin(self.blending.away_angle))

        # Draw heading
        renderer.set_pen(0xFF,0.02)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.heading_angle),
            arrow_length*sin(self.blending.heading_angle))
