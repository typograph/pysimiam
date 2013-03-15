"""
(c) PySimiam Team 2013

Contact person: Tim Fuchs <typograph@elec.ru>

This class was implemented for the weekly programming excercises
of the 'Control of Mobile Robots' course by Magnus Egerstedt.
"""
from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3BlendingSupervisor(K3Supervisor):
    """K3Blending supervisor uses a blending controller to make the robot reach the goal smoothly and without colliding wth walls."""
    def __init__(self, robot_pose, robot_info):
        """Create the controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        
        # Create the controller
        self.blending = self.create_controller('week5.Blending', self.ui_params)

        # Set the controller
        self.current = self.blending

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        K3Supervisor.set_parameters(self,params)
        self.blending.set_parameters(self.ui_params)

    def process(self):
        """Update state parameters for the controllers and self"""

        # The pose for controllers
        self.ui_params.pose = self.pose_est

        # Sensor readings in world units
        self.ui_params.sensor_distances = self.get_ir_distances()
        
        return self.ui_params
    
    def draw(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw(self,renderer)

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
        renderer.set_pen(0xAAAA00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.heading_angle),
            arrow_length*sin(self.blending.heading_angle))
