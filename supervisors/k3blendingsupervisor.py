#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from math import sqrt, sin, cos, atan2
from core.supervisor import Supervisor
from supervisors.khepera3 import K3Supervisor

class K3BlendingSupervisor(K3Supervisor):
    """K3Blending supervisor has two controllers - hold and blending, that blends
       go-to-goal and avoid-obstacles behaviour."""
    def __init__(self, robot_pose, robot_info):
        """Create controllers and the state transitions"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]

        # Add controllers
        self.blending = self.create_controller('blending.Blending', self.parameters)
        self.hold = self.create_controller('hold.Hold', None)
        
        # Transitions if at goal
        self.add_controller(self.hold,
                            (lambda: not self.at_goal(), self.blending))
        self.add_controller(self.blending,
                            (self.at_goal,self.hold))

        # Start in the 'blending' state
        self.current = self.blending

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        K3Supervisor.set_parameters(self,params)
        self.blending.set_parameters(self.parameters)

    def at_goal(self):
        """Check if the distance to goal is small"""
        return self.distance_from_goal < self.robot.wheels.base_length/2

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""
        K3Supervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.robot.pose
        
        # Distance to the goal
        self.distance_from_goal = sqrt((self.robot.pose.x - self.parameters.goal.x)**2 + (self.robot.pose.y - self.parameters.goal.y)**2)
        
        # Sensor readings in real units
        self.parameters.sensor_distances = self.get_ir_distances()
    
    def draw_foreground(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw_foreground(self,renderer)

        renderer.set_pose(self.robot.pose)
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
            