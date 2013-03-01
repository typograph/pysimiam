#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class BlendGTGAvoid(Controller):
    """Avoid obstacles is an example controller that checks the sensors for any readings, checks a threshold, and then performs counter-clockwise evasion from the first detected sensor position. Speed control and goal selection are a part of its routines."""
    def __init__(self, params):
        '''read another .xml for PID parameters?'''
        Controller.__init__(self,params)
        self.clear_error()

    def clear_error(self):
        self.E = 0
        self.error_1 = 0

    def set_parameters(self, params):
        """Set PID values
        @param: (float) kp, ki, kd
        """
        self.kp = params.gains.kp
        self.ki = params.gains.ki
        self.kd = params.gains.kd

        self.angles = params.sensor_angles
        self.weights = [(math.cos(a)+1.5) for a in self.angles]
        
    #User-defined function
    def calculate_new_goal(self, distances):
        """Determines a new goal for the robot based on which sensors are active"""
        
        angle = 0.0
        weightdist = 0.0
        
        maxdist = max(distances)
        mindist = min(distances)
        
        # Determine the angle with most obstacles
        
        if maxdist == mindist: # go forward
            angle = math.pi
        else:
            for s_angle, s_dist, s_weight in \
                zip(self.angles, distances, self.weights):
                
                angle += s_angle*(maxdist - s_dist)*s_weight
                weightdist += (maxdist - s_dist)*s_weight

            angle /= weightdist

        print angle

        # We have to escape, rotate by pi
        angle += self.robottheta + math.pi

        return angle

    def calculate_new_velocity(self, distances, vmax):
        """Adjusts robot velocity based on distance to object"""
        mindist = min(distances)
        maxdist = max(distances)
        
        # We want the robot to slow down as it approaches the obstacles
        # So, if mindist is real close to zero, the velocity should be
        # minimal, and if mindist is at maxdist, it can be maximal
        vel = (mindist/maxdist)*vmax
        return vmax

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params

        dt --> supervisor set timestep

        return --> unicycle model list [velocity, omega]"""
        self.robotx, self.roboty, self.robottheta = state.pose

        #Non-global goal
        theta_obstacles = self.calculate_new_goal(state.sensor_distances) #user defined function
        v_ = self.calculate_new_velocity(state.sensor_distances,
                                         state.velocity.v) #user defined function
                                         
        goal_x, goal_y = state.goal.x, state.goal.y
        theta_goal = math.atan2(goal_y - self.roboty, goal_x - self.robotx)

        # now instead of choosing one controller, blend results
        distmin = min(state.sensor_distances)
        distmax = state.sensor_max
        
        distance_ratio = distmin/distmax     
        if distance_ratio > 1:
            distance_ratio = 1
        # Forget about the goal at 0.2 ratio
        distance_ratio -= 0.2
        distance_ratio /= 0.8

        weight_avo = 0.5*(1 + math.cos(math.pi*distance_ratio))
        
        sum_y = math.sin(theta_obstacles)*weight_avo + math.sin(theta_goal)*(1-weight_avo)
        sum_x = math.cos(theta_obstacles)*weight_avo + math.cos(theta_goal)*(1-weight_avo)
        print weight_avo, sum_x, sum_y
        if math.sqrt(sum_x**2 + sum_y**2) > 0.05:
            theta = math.atan2(sum_y,sum_x)
        else:
            print math.sqrt(sum_x**2 + sum_y**2)
            if theta_obstacles > theta_goal:
                while theta_obstacles-theta_goal > math.pi:
                    theta_obstacles -= math.pi
            else:
                while theta_obstacles < theta_goal:
                    theta_obstacles += math.pi
            theta = (theta_obstacles + theta_goal)/2
            
        print theta_obstacles, theta_goal, theta

        #1. Calculate simple proportional error
        error = theta - self.robottheta

        #2. Correct for angles (angle may be greater than PI)
        error = math.atan2(math.sin(error), math.cos(error))

        #3. Calculate integral error
        self.E += error*dt

        #4. Calculate differential error
        dE = (error - self.error_1)/dt
        self.error_1 = error #updates the error_1 var

        #5. Calculate desired omega
        w_ = self.kp*error + self.ki*self.E + self.kd*dE

        #6. Return solution
        print v_, w_
        return [v_, w_]
