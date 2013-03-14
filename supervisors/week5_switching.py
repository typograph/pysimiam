from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3SwitchingSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Create necessary controllers"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]

        # Create the controllers
        # self.blending = self.create_controller('week5.Blending', self.ui_params)
        self.avoidobstacles = self.create_controller('AvoidObstacles', self.ui_params)
        self.gtg = self.create_controller('GoToGoal', self.ui_params)
        self.hold = self.create_controller('Hold', None)

        self.add_controller(self.hold)
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold))

        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment

        self.current = self.gtg

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.ui_params)
        self.avoidobstacles.set_parameters(self.ui_params)

    def at_goal(self):
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        return False
        
    def at_obstacle(self):
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        return False
        
    def obstacle_cleared(self):
        # Week 5 Assigment code should go here
        
        # End Week 5 Assignment
        return True

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.ui_params.sensor_distances = self.get_ir_distances()
        
        # Week 5 Assigment code can go here
        
        # End Week 5 Assignment
        
        # Ensure the headings are calculated
        self.avoidobstacles.get_heading(self.ui_params)
        self.gtg.get_heading(self.ui_params)

        return self.ui_params
    
    def draw(self, renderer):
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
            