#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from khepera3 import K3Supervisor
from simobject import Path
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3GTGSupervisor(K3Supervisor):
    """K3GTG supervisor uses one go-to-goal controller to make the robot reach the goal."""
    def __init__(self, robot_pose, robot_info):
        """Create the controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)
        
        # Create the tracker
        self.tracker = Path(robot_pose, 0)

        # Create the controller
        self.gtg = self.create_controller('week3.GoToGoal', self.parameters)

        # Set the controller
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        K3Supervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est
        
        # Update the trajectory
        self.tracker.add_point(self.pose_est)
    
    def draw(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw(self,renderer)

        # Draw robot path
        self.tracker.draw(renderer)
        
        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
        # Draw arrow to goal
        renderer.set_pen(0x00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.gtg.heading_angle),
            arrow_length*sin(self.gtg.heading_angle))
            
