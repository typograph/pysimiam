from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos

class K3DefaultSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        self.avoidobstacles = self.add_controller('avoidobstacles.AvoidObstacles', self.ui_params)
        self.gtg = self.add_controller('gotogoal.GoToGoal', self.ui_params.gains)
        self.hold = self.add_controller('hold.Hold', None)

        self.current = self.gtg

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(params.pid.gains)
        self.avoidobstacles.set_parameters(self.ui_params)

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est

        distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        if distance_from_goal < self.robot.wheels.base_length/2:
            if not self.current == self.hold:
                print "GOAL"
                self.current = self.hold
        else:
            self.ui_params.sensor_distances = self.get_ir_distances()
            distmin = min(self.ui_params.sensor_distances)
            if not self.current == self.gtg:
               if distmin > self.robot.ir_sensors.rmax/1.5:
                   print "GTG"
                   self.current = self.gtg
            elif not self.current == self.avoidobstacles:
               if distmin < self.robot.ir_sensors.rmax/2:
                   print "AVOID"
                   self.current = self.avoidobstacles
                   self.avoidobstacles.clear_error()

        self.avoidobstacles.calculate(self.ui_params)
        return self.ui_params
    
    def draw(self, renderer):
        K3Supervisor.draw(self,renderer)
        renderer.set_pose(self.pose_est)
        renderer.set_pen(0xFF0000)
        arrow_length = self.robot_size*5
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.avoidobstacles.away_angle),
            arrow_length*sin(self.avoidobstacles.away_angle))
            
        renderer.set_pen(0)
        for v in self.avoidobstacles.vectors:
            x,y,z = v
            renderer.draw_arrow(0,0,x,y)
            
