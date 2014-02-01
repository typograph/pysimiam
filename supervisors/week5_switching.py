#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3SwitchingSupervisor(K3Supervisor):
    """K3Switching supervisor switches between go-to-goal and avoid-obstacles controllers to make the robot reach the goal smoothly and without colliding wth walls."""
    def __init__(self, robot_pose, robot_info):
        """Create necessary controllers"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]

        # Create the controllers
        # self.blending = self.create_controller('week5.Blending', self.parameters)
        self.avoidobstacles = self.create_controller('AvoidObstacles', self.parameters)
        self.gtg = self.create_controller('GoToGoal', self.parameters)
        self.hold = self.create_controller('Hold', None)

        # Create some state transitions
        self.add_controller(self.hold)
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold))
        
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        
        # Start in 'go-to-goal' state
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)
        self.avoidobstacles.set_parameters(self.parameters)
        #self.blending.set_parameters(self.parameters)

    def at_goal(self):
        """Check if the distance to goal is small"""
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        return False
        
    def at_obstacle(self):
        """Check if the distance to obstacle is small"""
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        return False
        
    def obstacle_cleared(self):
        """Check if the distance to obstacle is large"""
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        return True

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        K3Supervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est
        # Sensor readings in real units
        self.parameters.sensor_distances = self.get_ir_distances()
        
        # Week 5 Assigment code can go here
        
        # End Week 5 Assignment
            
    def draw_foreground(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw_foreground(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5

        # Ensure the headings are calculated
        away_angle = self.avoidobstacles.get_heading_angle(self.parameters)
        goal_angle = self.gtg.get_heading_angle(self.parameters)
        
        # Draw arrow to goal
        if self.current == self.gtg:
            renderer.set_pen(0x00FF00)
        else:
            renderer.set_pen(0x2000FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.gtg.heading_angle),
            arrow_length*sin(self.gtg.heading_angle))

        # Draw arrow away from obstacles
        if self.current == self.avoidobstacles:
            renderer.set_pen(0xFF0000)
        else:
            renderer.set_pen(0x20FF0000)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.avoidobstacles.heading_angle),
            arrow_length*sin(self.avoidobstacles.heading_angle))

        if "blending" in self.__dict__:
            blend_angle = self.blending.get_heading_angle(self.parameters)
            # Draw the blending
            if self.current == self.avoidobstacles:
                renderer.set_pen(0xAAAA00)
            else:
                renderer.set_pen(0x20AAAA00)
            renderer.draw_arrow(0,0,
                arrow_length*cos(blending_angle),
                arrow_length*sin(blending_angle))
            