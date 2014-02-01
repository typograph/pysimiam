#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.quickbot import QuickBotSupervisor
from simobject import Path
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2
from pose import Pose

class QBGTGSupervisor(QuickBotSupervisor):
    """QBGTG supervisor uses one go-to-goal controller to make the robot reach the goal."""
    def __init__(self, robot_pose, robot_info):
        """Create the controller"""
        QuickBotSupervisor.__init__(self, robot_pose, robot_info)
        
        # Create the tracker
        self.tracker = Path(robot_pose, 0)

        # Create the controller
        self.gtg = self.create_controller('week3.GoToGoal', self.parameters)

        # Set the controller
        self.current = self.gtg

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        QuickBotSupervisor.set_parameters(self,params)
        self.gtg.set_parameters(self.parameters)

    def process_state_info(self, state):
        """Update state parameters for the controllers and self"""

        QuickBotSupervisor.process_state_info(self,state)

        # The pose for controllers
        self.parameters.pose = self.pose_est
        
        # Update the trajectory
        self.tracker.add_point(self.pose_est)

    def draw_background(self, renderer):
        """Draw controller info"""
        QuickBotSupervisor.draw_background(self,renderer)

        # Draw robot path
        self.tracker.draw(renderer)
            
    def draw_foreground(self, renderer):
        """Draw controller info"""
        QuickBotSupervisor.draw_foreground(self,renderer)
       
        renderer.set_pose(Pose(self.pose_est.x,self.pose_est.y))
        arrow_length = self.robot_size*5
        
        # Draw arrow to goal
        renderer.set_pen(0x00FF00)
        renderer.draw_arrow(0,0,
            arrow_length*cos(self.gtg.heading_angle),
            arrow_length*sin(self.gtg.heading_angle))

    def at_goal(self):
        distance_to_goal = sqrt( \
                                (self.pose_est.x - self.parameters.goal.x)**2
                              + (self.pose_est.y - self.parameters.goal.y)**2)
        
        return distance_to_goal < 0.02

            
    def ensure_w(self,v_lr):
      
        v_l, v_r = v_lr
        
        #Week 3 Assignment Code:
                
        #End Week 3 Assigment
        
        return v_l, v_r

    def execute(self, robot_info, dt):
        """Inherit default supervisor procedures and return unicycle model output (vl,vr)"""
        if not self.at_goal():
            output = Supervisor.execute(self, robot_info, dt)
            return self.ensure_w(self.uni2diff(output))
        else:
            return 0,0