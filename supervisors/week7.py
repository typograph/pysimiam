from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2
import numpy

class K3FullSupervisor(K3Supervisor):
    """K3Full supervisor creates four controllers: hold, gotogoal, avoidobstacles and blending."""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in some parameters
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        self.ui_params.ir_max = robot_info.ir_sensors.rmax
        self.ui_params.direction = 'left'
        self.ui_params.distance = 0.2
        
        self.robot = robot_info
        
        #Add controllers ( go to goal is default)
        self.avoidobstacles = self.create_controller('AvoidObstacles', self.ui_params)
        self.gtg = self.create_controller('GoToGoal', self.ui_params)
        #self.wall = self.create_controller('FollowWall', self.ui_params)
        self.hold = self.create_controller('Hold', None)
        
        self.add_controller(self.hold,
                            (lambda: not self.at_goal(), self.gtg))
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold),
                            (self.at_obstacle, self.avoidobstacles))
        self.add_controller(self.avoidobstacles,
                            (self.at_goal, self.hold),
                            (self.free, self.gtg),
                            )

        self.current = self.gtg

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.ui_params)
        self.avoidobstacles.set_parameters(self.ui_params)
        self.wall.set_parameters(self.ui_params)

    def at_goal(self):
        return self.distance_from_goal < self.robot.wheels.base_length/2

    def at_obstacle(self):
        return self.distmin < self.robot.ir_sensors.rmax*0.5
        
    def free(self):
        return self.distmin > self.robot.ir_sensors.rmax*0.75

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        
        self.ui_params.sensor_distances = self.get_ir_distances()       
        self.distmin = min(self.ui_params.sensor_distances)

        return self.ui_params
    
    def draw(self, renderer):
        K3Supervisor.draw(self,renderer)

        # Make sure to have all headings:
        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5

        if self.current == self.gtg:
            # Draw arrow to goal
            renderer.set_pen(0x00FF00)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.gtg.heading_angle),
                arrow_length*sin(self.gtg.heading_angle))

        elif self.current == self.avoidobstacles:
            # Draw arrow away from obstacles
            renderer.set_pen(0xFF0000)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.avoidobstacles.heading_angle),
                arrow_length*sin(self.avoidobstacles.heading_angle))

        elif self.current == self.wall:

            # Draw vector to wall:
            renderer.set_pen(0x0000FF)
            renderer.draw_arrow(0,0,
                self.wall.to_wall_vector[0],
                self.wall.to_wall_vector[1])
            # Draw 
            renderer.set_pen(0xFF00FF)
            renderer.push_state()
            renderer.translate(self.wall.to_wall_vector[0], self.wall.to_wall_vector[1])
            renderer.draw_arrow(0,0,
                self.wall.along_wall_vector[0],
                self.wall.along_wall_vector[1])
            renderer.pop_state()

            # Draw heading (who knows, it might not be along_wall)
            renderer.set_pen(0xFF00FF)
            renderer.draw_arrow(0,0,
                arrow_length*cos(self.wall.heading_angle),
                arrow_length*sin(self.wall.heading_angle))
