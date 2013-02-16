"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: Example PID implementation for goal-seek (incomplete)
"""
from controller import Controller
import math
import numpy

class AvoidObstacles(Controller):
    def __init__(self):
        '''read another .xml for PID parameters?'''
        self.kp=10
        self.ki=0
        self.kd=0

        self.E = 0
        self.error_1 = 0

    def set_parameters(self, params):
        """Set PID values
        @param: (float) kp, ki, kd
        """
        self.kp = params.kp
        self.ki = params.ki
        self.kd = params.kd

    #User-defined function
    def calculate_new_goal(ir_distances):
        # 
        pass

    def calculate_new_velocity(ir_distances):
        #Compare values to range
        for dist in ir_distances:
            if dist < 100:
                return 10

        #if nothing found
        return 100

    def execute(self, state, dt):
        #Select a goal, ccw obstacle avoidance
        #Get distances from sensors 
        ir_distances = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] 

        robotx, roboty, robottheta = state.pose
        goalx, goaly = state.goalx, state.goaly
    
        goal = self.calculate_new_goal(ir_distances) #user defined function
        v_ = self.calculate_new_velocity(ir_distances) #user defined function

        #Calculate simple proportional error
        error = math.atan2(goaly - roboty, goalx - robotx) - robottheta 
        error = math.atan2(math.sin(error), math.cos(error))

        #Calculate integral error
        self.E += error*dt

        #Calculate differential error
        dE = error - self.error_1
        self.error_1 = error #updates the error_1 var

        #Calculate desired omega
        w_ = self.kp*error + self.ki*self.E + self.kd*dE

        #Return solution
        return [v_, w_]
