"""
(c) PySimiam Team 2013

Contact person: Tim Fuchs <typograph@elec.ru>

This class was implemented for the weekly programming excercises
of the 'Control of Mobile Robots' course by Magnus Egerstedt.
"""
from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3SwitchingSupervisor(K3Supervisor):
    """K3Switching supervisor switches between go-to-goal and avoid-obstacles controllers to make the robot reach the goal smoothly and without colliding wth walls."""
    def __init__(self, robot_pose, robot_info):
        """Create necessary controllers"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]

        # Create the controllers
        # self.blending = self.create_controller('week5.Blending', self.ui_params)
        self.avoidobstacles = self.create_controller('AvoidObstacles', self.ui_params)
        self.gtg = self.create_controller('GoToGoal', self.ui_params)
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
        self.gtg.set_parameters(self.ui_params)
        self.avoidobstacles.set_parameters(self.ui_params)
        #self.blending.set_parameters(self.ui_params)

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

    def process(self):
        """Update state parameters for the controllers and self"""

        # The pose for controllers
        self.ui_params.pose = self.pose_est
        # Sensor readings in real units
        self.ui_params.sensor_distances = self.get_ir_distances()
        
        # Week 5 Assigment code can go here
        
        # End Week 5 Assignment
        
        # Ensure the headings are calculated
        self.avoidobstacles.get_heading(self.ui_params)
        self.gtg.get_heading(self.ui_params)
        #self.blending.get_heading(self.ui_params)

        return self.ui_params
    
    def draw(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
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
            # Draw the blending
            if self.current == self.avoidobstacles:
                renderer.set_pen(0xAAAA00)
            else:
                renderer.set_pen(0x20AAAA00)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.blending.heading_angle),
                arrow_length*sin(self.blending.heading_angle))
            