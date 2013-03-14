from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3GTGSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)
        self.tracker = Path(robot_pose, 0)
                    
        self.gtg = self.create_controller('week3.GoToGoal', self.ui_params)

        self.current = self.gtg

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.ui_params)

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.tracker.add_point(self.pose_est)
        return self.ui_params
    
    def draw(self, renderer):
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
            
