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
	self.weights = [1]*len(self.angles)

    #User-defined function
    def calculate_new_goal(self, distances):
        """Determines a new goal for the robot based on which sensors are active"""
        angle = 0.0
        weightdist = 0.0
        for i in range(len(distances)):
            angle += self.angles[i]*distances[i]*self.weights[i]
            weightdist += distances[i]*self.weights[i] 

        angle = angle/weightdist #average angle to the clear
        angle = angle + self.robottheta

        #if angle < 0.0:
        #    angle += 2*math.pi
        #elif angle > 2*math.pi:
        #    angle -= 2*math.pi

        print angle
        return angle 
        

    def calculate_new_velocity(self, distances):
        """Adjusts robot velocity based on distance to object"""
        mindist = min(distances)
        
        vel = max(min(mindist/0.29*0.4, 0.4), 0.1) 
        return vel 

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params

        dt --> supervisor set timestep

        return --> unicycle model list [velocity, omega]"""
        self.robotx, self.roboty, self.robottheta = state.pose

        #Non-global goal
        theta = self.calculate_new_goal(state.sensor_distances) #user defined function
        v_ = self.calculate_new_velocity(state.sensor_distances) #user defined function

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
        return [v_, w_]
