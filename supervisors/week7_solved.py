#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.quickbot import QuickBotSupervisor
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2
from ui import uiFloat
import numpy

class QBFullSupervisor(QuickBotSupervisor):
    """QBFull supervisor implements the full switching behaviour for navigating labyrinths."""
    def __init__(self, robot_pose, robot_info, options = None):
        """Create controllers and the state transitions"""
        QuickBotSupervisor.__init__(self, robot_pose, robot_info)

        self.extgoal = False

        if options is not None:
            try:
                self.parameters.goal.x = options.x
                self.parameters.goal.y = options.y
                self.extgoal = True
            except Exception:
                pass
            
        # Fill in some parameters
        self.parameters.sensor_poses = robot_info.ir_sensors.poses[:]
        self.parameters.ir_max = robot_info.ir_sensors.rmax
        self.parameters.direction = 'left'
        self.parameters.distance = 0.2
        
        self.robot = robot_info
        
        #Add controllers
        self.avoidobstacles = self.create_controller('AvoidObstacles', self.parameters)
        self.gtg = self.create_controller('GoToGoal', self.parameters)
        self.wall = self.create_controller('FollowWall', self.parameters)
        self.hold = self.create_controller('Hold', None)

        # Week 7 Assignment:
        
        # Define transitions
        self.add_controller(self.hold,
                            (lambda: not self.at_goal(), self.gtg))
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold),
                            (self.unsafe, self.avoidobstacles),
                            (lambda: self.at_obstacle() and not self.detach(), self.wall))
        self.add_controller(self.avoidobstacles,
                            (self.at_goal, self.hold),
                            (self.safe, self.gtg))
        self.add_controller(self.wall,
                            (self.at_goal, self.hold),
                            (lambda: self.progress_made() and self.detach(), self.gtg))
#                            (self.unsafe, self.avoidobstacles))
        
        # Change and add additional transitions
        
        # End Week 7

        # Start in the 'go-to-goal' state
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        QuickBotSupervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)
        self.avoidobstacles.set_parameters(self.parameters)
        self.wall.set_parameters(self.parameters)

    def at_goal(self):
        """Check if the distance to goal is small"""
        return self.distance_from_goal < 0.05

    def at_obstacle(self):
        """Check if the distance to obstacle is small"""
        atobst =  self.distmin < self.robot.ir_sensors.rmax/1.1
        if atobst:
            ind_dmin = list(self.parameters.sensor_distances).index(self.distmin)
            if ind_dmin > 2:
                self.parameters.direction = 'right'
            elif ind_dmin < 2:
                self.parameters.direction = 'left'
            else:
                return False
            self.progress = self.distance_from_goal
        return atobst

    def unsafe(self):
        """Check if we are too close to the wall for safe cruising"""
        return self.distmin < self.robot.ir_sensors.rmin*2.0 or \
               self.parameters.sensor_distances[2] < self.robot.ir_sensors.rmax/2.0
        
    def safe(self):
        return self.distmin > self.robot.ir_sensors.rmin*4.0
    
    def progress_made(self):
        """Check if we a re closer to the goal than before"""
        return self.distance_from_goal < self.progress

    def detach(self):
        """Check if detatching from the wall makes sense (the goal is on the right side"""
        goal_angle = self.gtg.get_heading_angle(self.parameters)
        wall_angle = self.wall.get_heading_angle(self.parameters)
        if goal_angle > wall_angle and self.parameters.direction == "right":
            return True
        if goal_angle < wall_angle and self.parameters.direction == "left":
            return True
        return False

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        QuickBotSupervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est

        # Distance to the goal
        self.distance_from_goal = sqrt((self.pose_est.x - self.parameters.goal.x)**2 + (self.pose_est.y - self.parameters.goal.y)**2)
        
        # Sensor readings in real units
        self.parameters.sensor_distances = self.get_ir_distances()
        
        # Distance to the closest obstacle        
        self.distmin = min(self.parameters.sensor_distances)

    def draw_foreground(self, renderer):
        """Draw controller info"""
        QuickBotSupervisor.draw_foreground(self,renderer)

        # Make sure to have all headings:
        renderer.set_pose(self.pose_est)
        arrow_length = self.robot_size*5

        # Ensure the headings are calculated
        
        # Draw arrow to goal
        if self.current == self.gtg:
            goal_angle = self.gtg.get_heading_angle(self.parameters)
            renderer.set_pen(0x00FF00)
            renderer.draw_arrow(0,0,
                arrow_length*cos(goal_angle),
                arrow_length*sin(goal_angle))

        # Draw arrow away from obstacles
        elif self.current == self.avoidobstacles:
            away_angle = self.avoidobstacles.get_heading_angle(self.parameters)
            renderer.set_pen(0xCC3311)
            renderer.draw_arrow(0,0,
                arrow_length*cos(away_angle),
                arrow_length*sin(away_angle))

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

    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
        if p is None:
            p = self.parameters
        
        ui =   [('goal', [('x',uiFloat(p.goal.x,0.1)), ('y',uiFloat(p.goal.y,0.1))]),
                ('velocity', [('v',uiFloat(p.velocity.v,0.1))]),
                (('gains',"PID gains"), [
                    (('kp','Proportional gain'), uiFloat(p.gains.kp,0.1)),
                    (('ki','Integral gain'), uiFloat(p.gains.ki,0.1)),
                    (('kd','Differential gain'), uiFloat(p.gains.kd,0.1))])]
                
        if self.extgoal:
            return ui[1:]
        else:
            return ui
