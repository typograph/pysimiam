#
# (c) PySimiam Team 2014
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.quickbot import QuickBotSupervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class QuickBotDefaultSupervisor(QuickBotSupervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles.
       It switches between the two depending on the distance to the closest
       obstacle."""
    def __init__(self, robot_pose, robot_info):
        """Create controllers and the state transitions"""
        QuickBotSupervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]

        # Add controllers
        self.gtg = self.create_controller('gotogoal.GoToGoal', self.parameters)
        self.hold = self.create_controller('hold.Hold', None)

        # Transitions if at goal/obstacle
        self.add_controller(self.hold, (lambda : not self.at_goal(), self.gtg))
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold))

        # Start in the 'go-to-goal' state
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        QuickBotSupervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)

    def at_goal(self):
        """Check if the distance to goal is small"""
        return self.distance_from_goal < self.robot.wheels.base_length/2
        
    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        QuickBotSupervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est
        # Sensor readings in real units
        self.parameters.sensor_distances = self.get_ir_distances()
        
        # Distance to the goal
        self.distance_from_goal = sqrt((self.pose_est.x - self.parameters.goal.x)**2 + (self.pose_est.y - self.parameters.goal.y)**2)
          
        return self.parameters
    
    def draw(self, renderer):
        """Draw controller info"""
        QuickBotSupervisor.draw(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5

        goal_angle = self.gtg.get_heading_angle(self.parameters)
        
        # Draw arrow to goal
        renderer.set_pen(0x00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(goal_angle),
            arrow_length*sin(goal_angle))
            