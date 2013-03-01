#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from controller import Controller
import math
import numpy

class AvoidObstacles(Controller):
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
                
            #angle /= maxdist - mindist
            angle /= weightdist

        print angle

        # We have to escape, rotate by pi
        angle += self.robottheta + math.pi

        #angle = angle/weightdist #average angle to the clear

        return (angle+math.pi)%(2*math.pi) - math.pi

    def calculate_new_velocity(self, distances, vmax):
        """Adjusts robot velocity based on distance to object"""
        mindist = min(distances)
        maxdist = max(distances)
        
        # We want the robot to slow down as it approaches the obstacles
        # So, if mindist is real close to zero, the velocity should be
        # minimal, and if mindist is at maxdist, it can be maximal
        vel = math.sqrt(mindist/maxdist)*vmax
        return vel 

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params

        dt --> supervisor set timestep

        return --> unicycle model list [velocity, omega]"""
        self.robotx, self.roboty, self.robottheta = state.pose

        #Non-global goal
        theta = self.calculate_new_goal(state.sensor_distances) #user defined function
        v_ = self.calculate_new_velocity(state.sensor_distances,
                                         state.velocity.v) #user defined function

        #1. Calculate simple proportional error
        error = theta - self.robottheta

        #2. Correct for angles (angle may be greater than PI)
        error = math.atan2(math.sin(error), math.cos(error))

        #3. Calculate integral error
        self.E += error*dt
        self.E = (self.E + math.pi)%(2*math.pi) - math.pi

        #4. Calculate differential error
        dE = (error - self.error_1)/dt
        self.error_1 = error #updates the error_1 var

        #5. Calculate desired omega
        w_ = self.kp*error + self.ki*self.E + self.kd*dE

        #6. Return solution
        return [v_, w_]
