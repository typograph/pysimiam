#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from math import sqrt, sin, cos, atan2
import numpy
from core.supervisor import Supervisor
from supervisors.khepera3 import K3Supervisor

class K3FullSupervisor(K3Supervisor):
    """K3Full supervisor implements the full switching behaviour for navigating labyrinths."""
    def __init__(self, robot_pose, robot_info):
        """Create controllers and the state transitions"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        # The maximal distance to an obstacle (inexact)
        self.distmax = robot_info.ir_sensors.rmax + robot_info.wheels.base_length/2

        # Fill in some parameters
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]
        self.parameters.ir_max = robot_info.ir_sensors.rmax
        self.parameters.direction = 'left'
        self.parameters.distance = self.distmax*0.85
        
        self.process_state_info(robot_info)
        
        #Add controllers
        self.gtg = self.create_controller('GoToGoal', self.parameters)
        self.avoidobstacles = self.create_controller('AvoidObstacles', self.parameters)
        self.wall = self.create_controller('FollowWall', self.parameters)
        self.hold = self.create_controller('Hold', None)
        
        # Define transitions
        self.add_controller(self.hold,
                            (lambda: not self.at_goal(), self.gtg))
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold),
                            (self.at_wall, self.wall))
        self.add_controller(self.wall,
                            (self.at_goal,self.hold),
                            (self.unsafe, self.avoidobstacles),
                            (self.wall_cleared, self.gtg))
        self.add_controller(self.avoidobstacles,
                            (self.at_goal, self.hold),
                            (self.safe, self.wall))

        # Start in the 'go-to-goal' state
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)
        self.avoidobstacles.set_parameters(self.parameters)
        self.wall.set_parameters(self.parameters)

    def at_goal(self):
        """Check if the distance to goal is small"""
        return self.distance_from_goal < self.robot.wheels.base_length/2

    def is_at_wall(self):
        """Check if the distance to wall is small"""
        return self.distmin < self.distmax*0.8

    def at_wall(self):
        """Check the distance to wall and decide
           on the direction"""

        wall_close = self.is_at_wall()
        
        # Decide which direction to go
        if wall_close:
        
            # Find the closest detected point
            dmin = self.distmax
            tmin = 0
            for i, d in enumerate(self.parameters.sensor_distances):
                if d < dmin:
                    dmin = d
                    tmin = self.parameters.sensor_poses[i].theta
            
            # Go that way
            if tmin > 0:
                self.parameters.direction = 'left'
            else:
                self.parameters.direction = 'right'
              
            # Notify the controller
            self.wall.set_parameters(self.parameters)
            
            # Save the closest we've been to the goal
            self.best_distance = self.distance_from_goal
            
        return wall_close

    def wall_cleared(self):
        """Check if the robot should stop following the wall"""

        # Did we make progress?
        if self.distance_from_goal >= self.best_distance:
            return False
            
        self.best_distance = self.distance_from_goal

        # Are we far enough from the wall,
        # so that we don't switch back immediately
        if self.is_at_wall():
            return False
            
        # Check if we have a clear shot to the goal
        theta_gtg = self.gtg.get_heading_angle(self.parameters)
        
        if self.parameters.direction == 'left':
            return sin(theta_gtg - self.wall.heading_angle) <= 0
        else:
            return sin(theta_gtg - self.wall.heading_angle) >= 0

    def unsafe(self):
        """Check if the distance to wall is too small"""        
        return self.distmin < self.distmax*0.5
        
    def safe(self):
        """Check if the distance to wall is ok again"""        
        wall_far = self.distmin > self.distmax*0.6
        # Check which way to go
        if wall_far:
            self.at_wall()
        return wall_far

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        K3Supervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.robot.pose
        
        # Distance to the goal
        self.distance_from_goal = sqrt((self.robot.pose.x - self.parameters.goal.x)**2 + (self.robot.pose.y - self.parameters.goal.y)**2)
        
        # Sensor readings in real units
        self.parameters.sensor_distances = self.get_ir_distances()
        
        # Smallest reading translated into distance from center of robot
        vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(self.parameters.sensor_distances, self.parameters.sensor_poses) \
                     if abs(p.theta) < 2.4] )
        
        self.distmin = min((sqrt(a[0]**2 + a[1]**2) for a in vectors))
    
    def draw_foreground(self, renderer):
        """Draw controller info"""
        K3Supervisor.draw_foreground(self,renderer)

        renderer.set_pose(self.robot.pose)
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

            # Important sensors
            renderer.set_pen(0)
            for v in self.wall.vectors:
                x,y,z = v
                
                renderer.push_state()
                renderer.translate(x,y)
                renderer.rotate(atan2(y,x))
            
                renderer.draw_line(0.01,0.01,-0.01,-0.01)
                renderer.draw_line(0.01,-0.01,-0.01,0.01)
                
                renderer.pop_state()