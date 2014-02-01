#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.week3 import GoToGoal
import math
import numpy

class GoToGoalX(GoToGoal):
    """Go-to-goal steers the robot to a predefined position in the world."""

    def get_heading_angle(self, state):
        """Get the heading angle in the world frame of reference."""
        
        #Insert Week 3 Assignment Code Here
        # Here is an example of how to get goal position
        # and robot pose data. Feel free to name them differently.
        
        x_g, y_g = state.goal.x, state.goal.y
        x_r, y_r, theta = state.pose
        
        return math.atan2(y_g-y_r,x_g-x_r)
        #End Week 3 Assigment        

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt.
        state --> the state of the robot and the goal
        dt --> elapsed time
        return --> unicycle model list [velocity, omega]"""
        
        self.heading_angle = self.get_heading_angle(state)
        
        # 1. Calculate simple proportional error
        # The direction is in the world frame of reference
        # Note that the error is adjusted to the region between pi and -pi.
        error = (self.heading_angle - state.pose.theta + math.pi)%(2*math.pi) - math.pi

        # 2. Calculate integral error
        self.E += error*dt
        self.E = (self.E + math.pi)%(2*math.pi) - math.pi

        # 3. Calculate differential error
        dE = (error - self.e_1)/dt
        self.e_1 = error #updates the e_1 var

        # 4. Calculate desired omega
        w_ = self.kp*error + self.ki*self.E + self.kd*dE
        
        # The linear velocity is given to us:
        return (state.velocity.v, w_)