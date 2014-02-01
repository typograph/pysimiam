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

class K3AvoidSupervisor(K3Supervisor):
    """K3Avoid supervisor uses one avoid-obstacles controller to drive the robot through a cluttered environment without collisions."""
    def __init__(self, robot_pose, robot_info):
        """Create the controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]

        # Create the controller
        self.avoidobstacles = self.create_controller('week4.AvoidObstacles', self.parameters)

        # Set the controller
        self.current = self.avoidobstacles

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        self.parameters.velocity = params.velocity
        self.parameters.gains = params.gains
        self.avoidobstacles.set_parameters(self.parameters)

    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
        if p is None:
            p = self.parameters
        
        return [('velocity', [('v', p.velocity.v)]),
                (('gains',"PID gains"),
                    [(('kp','Proportional gain'), p.gains.kp),
                     (('ki','Integral gain'), p.gains.ki),
                     (('kd','Differential gain'), p.gains.kd)])]

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        K3Supervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est

        # Sensor readings in world units
        self.parameters.sensor_distances = self.get_ir_distances()
    
    def draw_foreground(self, renderer):
        """Draw controller info"""

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5
        
        # Draw arrow away from obstacles
        renderer.set_pen(0xCC3311)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.avoidobstacles.heading_angle),
            arrow_length*sin(self.avoidobstacles.heading_angle))
            
        # Draw calculated vectors
        renderer.set_pen(0)
        for v in self.avoidobstacles.vectors:
            x,y,z = v
            
            renderer.push_state()
            renderer.translate(x,y)
            renderer.rotate(atan2(y,x))
        
            renderer.draw_line(0.01,0.01,-0.01,-0.01)
            renderer.draw_line(0.01,-0.01,-0.01,0.01)
            
            renderer.pop_state()
            
