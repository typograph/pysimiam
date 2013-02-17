"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: Example PID implementation for goal-seek (incomplete)
"""
from controller import Controller
import math
import numpy

class AvoidObstacles(Controller):
    def __init__(self, params):
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
    def calculate_new_goal(self, ir_readings):
        #Normalize the angle values
        ir_angles = [128, 75, 42, 13, -13, -42, -75, -128, 180]

        #travel orthogonally unless more then one point detected
        objlist = []
        for i in range(0, len(ir_readings)):
            if ir_readings[i] > 100:
                objlist.append(i)
            
        numobjects = len(objlist)
        if numobjects > 1: # simple go 90 degrees from object
            index = objlist[0]
            angle = ir_angles[index] + 90
            angle = math.radians(angle)
            angle = math.atan2(math.sin(angle), math.cos(angle))
            goalx = self.robotx + 100*math.cos(self.robottheta + angle)
            goaly = self.robotx + 100*math.sin(self.robottheta + angle)
            return (goalx, goaly)
        
        return (self.goalx, self.goaly)

    def calculate_new_velocity(self, ir_distances):
        #Compare values to range
        for dist in ir_distances:
            if dist > 100:
                return 0.1 

        #if nothing found
        return 0.4 

    def execute(self, state, dt):
        #Select a goal, ccw obstacle avoidance

        self.robotx, self.roboty, self.robottheta = state.pose
        self.goalx, self.goaly = state.goal.x, state.goal.y
    
        #Non-global goal
        goalx, goaly = self.calculate_new_goal(state.ir_distances) #user defined function
        v_ = self.calculate_new_velocity(state.ir_distances) #user defined function

        #1. Calculate simple proportional error
        error = math.atan2(goaly - self.roboty, goalx - self.robotx) - self.robottheta 

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
