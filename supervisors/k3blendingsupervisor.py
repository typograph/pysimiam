from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3BlendingSupervisor(K3Supervisor):
    """K3Blending supervisor has just one controller, the one that blends between the creates four controllers: hold, gotogoal, avoidobstacles and blending."""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        self.blending = self.get_controller('blending.Blending', self.ui_params)
        self.hold = self.get_controller('hold.Hold', None)
        
        self.add_controller(self.hold,
                            (lambda: not self.at_goal(), self.blending))
        self.add_controller(self.blending,
                            (self.at_goal,self.hold))

        self.current = self.blending

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.blending.set_parameters(self.ui_params)

    def at_goal(self):
        return self.distance_from_goal < self.robot.wheels.base_length/2

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        
        self.ui_params.sensor_distances = self.get_ir_distances()
        self.distmin = min(
            (d for d, p in zip(self.ui_params.sensor_distances, self.ui_params.sensor_poses) if abs(p.theta) < 2.2))

        return self.ui_params
    
    def draw(self, renderer):
        K3Supervisor.draw(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
        # Draw arrow to goal
        renderer.set_pen(0x00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.goal_angle),
            arrow_length*sin(self.blending.goal_angle))

        # Draw arrow away from obstacles
        renderer.set_pen(0xFF0000)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.away_angle),
            arrow_length*sin(self.blending.away_angle))

        # Draw heading
        renderer.set_pen(0x0000FF)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.blending.heading_angle),
            arrow_length*sin(self.blending.heading_angle))
            