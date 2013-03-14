from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2
from collections import OrderedDict

class K3AvoidSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]

        self.avoidobstacles = self.create_controller('week4.AvoidObstacles', self.ui_params)

        self.current = self.avoidobstacles

    def set_parameters(self,params):
        self.ui_params.velocity = params.velocity
        self.ui_params.gains = params.gains
        self.avoidobstacles.set_parameters(self.ui_params)

    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
        if p is None:
            p = self.ui_params
        
        return OrderedDict([
                    ('velocity', {'v':p.velocity.v}),
                    (('gains',"PID gains"), OrderedDict([
                        (('kp','Proportional gain'), p.gains.kp),
                        (('ki','Integral gain'), p.gains.ki),
                        (('kd','Differential gain'), p.gains.kd)]))])

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est
        self.ui_params.sensor_distances = self.get_ir_distances()

        return self.ui_params
    
    def draw(self, renderer):
        # Draw robot path
        self.tracker.draw(renderer)
        
        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
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
            
