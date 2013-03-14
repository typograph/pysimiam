from khepera3 import K3Supervisor
from helpers import Struct
from numpy import array, dot
from collections import OrderedDict

from math import pi, sin, cos, log1p, sqrt, atan2

class K3WallSupervisor(K3Supervisor):
    """The K3DebugSupervisor stays at the wall."""
    def __init__(self, robot_pose, robot_info):
        K3Supervisor.__init__(self, robot_pose, robot_info)

        self.ui_params.sensor_poses = robot_info.ir_sensors.poses[:]
        
        # Create controllers
        self.current = self.create_controller('week6.FollowWall', self.ui_params)

    def set_parameters(self,params):
        self.ui_params.direction = params.wall.direction
        self.ui_params.distance = params.wall.distance
        self.ui_params.velocity = params.velocity
        self.ui_params.gains = params.gains
        self.current.set_parameters(self.ui_params)
    
    def get_parameters(self):
        p = Struct()
        p.wall = Struct()
        p.wall.direction = self.ui_params.direction
        p.wall.distance = self.ui_params.distance
        p.velocity = self.ui_params.velocity
        p.gains = self.ui_params.gains
        return p        

    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
        if p is None:
            p = self.ui_params
        
        return OrderedDict([
                    (('wall', "Follow wall"), OrderedDict([
                        ('direction', (p.direction,['left','right'])),
                        (('distance','Distance to wall'), p.distance)])),
                    ('velocity', {'v':p.velocity.v}),
                    (('gains',"PID gains"), OrderedDict([
                        (('kp','Proportional gain'), p.gains.kp),
                        (('ki','Integral gain'), p.gains.ki),
                        (('kd','Differential gain'), p.gains.kd)]))])
                    
    def get_default_parameters(self):
        """Sets the default PID parameters, goal, and velocity"""
        p = Struct()
        p.direction = 'left'
        p.distance = 0.2
        p.velocity = Struct()
        p.velocity.v = 0.2
        p.gains = Struct()
        p.gains.kp = 10.0
        p.gains.ki = 2.0
        p.gains.kd = 0.0
        return p

    def process(self):
        """Select controller and insert data into a state info structure for the controller"""
        self.ui_params.sensor_distances = self.get_ir_distances()

        return self.ui_params
    
    def draw(self, renderer):
        
        """Draw follow wall"""
        renderer.set_pose(self.pose_est)
        arrow_length = self.robot.wheels.base_length*5
        
        # Draw vector to wall:
        if self.current.to_wall_vector is not None:
            renderer.set_pen(0x0000FF)
            renderer.draw_arrow(0,0,
                self.current.to_wall_vector[0],
                self.current.to_wall_vector[1])
            # Draw 
            if self.current.along_wall_vector is not None:
                renderer.set_pen(0xFF00FF)
                renderer.push_state()
                renderer.translate(self.current.to_wall_vector[0], self.current.to_wall_vector[1])
                renderer.draw_arrow(0,0,
                    self.current.along_wall_vector[0],
                    self.current.along_wall_vector[1])
                renderer.pop_state()

        # Draw heading (who knows, it might not be along_wall)
        renderer.set_pen(0x000000)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.current.heading_angle),
            arrow_length*sin(self.current.heading_angle))

        # Important sensors
        renderer.set_pen(0)
        for v in self.current.vectors:
            x,y,z = v
            
            renderer.push_state()
            renderer.translate(x,y)
            renderer.rotate(atan2(y,x))
        
            renderer.draw_line(0.01,0.01,-0.01,-0.01)
            renderer.draw_line(0.01,-0.01,-0.01,0.01)
            
            renderer.pop_state()                           
        