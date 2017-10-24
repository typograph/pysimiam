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

class K3DefaultSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles.
       It switches between the two depending on the distance to the closest
       obstacle."""
    def __init__(self, robot_pose, robot_info):
        """Create controllers and the state transitions"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # Fill in poses for the controller
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]

        # Add controllers
        self.avoidobstacles = self.create_controller('avoidobstacles.AvoidObstacles', self.parameters)
        self.gtg = self.create_controller('gotogoal.GoToGoal', self.parameters)
        self.hold = self.create_controller('hold.Hold', None)

        # Transitions if at goal/obstacle
        self.add_controller(self.hold)
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold),
                            (self.at_obstacle, self.avoidobstacles))
        self.add_controller(self.avoidobstacles,
                            (self.at_goal, self.hold),
                            (self.free, self.gtg),
                            )

        # Start in the 'go-to-goal' state
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)
        self.avoidobstacles.set_parameters(self.parameters)

    def at_goal(self):
        """Check if the distance to goal is small"""
        return self.distance_from_goal < self.robot.wheels.base_length/2
        
    def at_obstacle(self):
        """Check if the distance to obstacle is small"""
        return self.distmin < self.robot.ir_sensors.rmax/2
        
    def free(self):
        """Check if the distance to obstacle is large"""
        return self.distmin > self.robot.ir_sensors.rmax/1.5

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        K3Supervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est
        # Sensor readings in real units
        self.parameters.sensor_distances = self.get_ir_distances()
        
        # Distance to the goal
        self.distance_from_goal = sqrt((self.pose_est.x - self.parameters.goal.x)**2 + (self.pose_est.y - self.parameters.goal.y)**2)
        
        # Distance to the closest obstacle
        self.distmin = min(self.parameters.sensor_distances)
        
        return self.parameters
    
    def draw_foreground(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw_foreground(self,renderer)

        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5

        away_angle = self.avoidobstacles.get_heading_angle(self.parameters)
        goal_angle = self.gtg.get_heading_angle(self.parameters)
        
        # Draw arrow to goal
        renderer.set_pen(0x00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(goal_angle),
            arrow_length*sin(goal_angle))

        # Draw arrow away from obstacles
        renderer.set_pen(0xFF0000)
        renderer.draw_arrow(0,0,
            arrow_length*cos(away_angle),
            arrow_length*sin(away_angle))
            