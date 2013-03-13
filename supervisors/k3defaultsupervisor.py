from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class K3DefaultSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        self.avoidobstacles = self.get_controller('avoidobstacles.AvoidObstacles', self.ui_params)
        self.gtg = self.get_controller('gotogoal.GoToGoal', self.ui_params)
        self.hold = self.get_controller('hold.Hold', None)

        self.add_controller(self.hold)
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

    def at_goal(self):
        return self.distance_from_goal < self.robot.wheels.base_length/2
        
    def at_obstacle(self):
        return self.distmin < self.robot.ir_sensors.rmax/2
        
    def free(self):
        return self.distmin > self.robot.ir_sensors.rmax/1.5

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.ui_params.sensor_distances = self.get_ir_distances()
        
        self.distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        self.distmin = min(self.ui_params.sensor_distances)
        
        # Ensure the headings are calculated
        self.avoidobstacles.get_heading(self.ui_params)
        self.gtg.get_heading(self.ui_params)

        return self.ui_params
    
    def draw(self, renderer):
        K3Supervisor.draw(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
        # Draw arrow to goal
        renderer.set_pen(0x00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.gtg.heading_angle),
            arrow_length*sin(self.gtg.heading_angle))

        # Draw arrow away from obstacles
        renderer.set_pen(0xFF0000)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.avoidobstacles.heading_angle),
            arrow_length*sin(self.avoidobstacles.heading_angle))
            
        # Week 3
        renderer.set_pen(0)
        for v in self.avoidobstacles.vectors:
            x,y,z = v
            
            renderer.push_state()
            renderer.translate(x,y)
            renderer.rotate(atan2(y,x))
        
            renderer.draw_line(0.01,0.01,-0.01,-0.01)
            renderer.draw_line(0.01,-0.01,-0.01,0.01)
            
            renderer.pop_state()            
            
