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
        self.kp=10
        self.ki=0
        self.kd=0

        self.E = 0
        self.error_1 = 0

        self.ir_angles = [
        math.radians(128), 
        math.radians(75),
        math.radians(42), 
        math.radians(13), 
        math.radians(-13),
        math.radians(-42),
        math.radians(-75),
        math.radians(-128),
        math.radians(180) ]

        self.ir_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1]

    def set_parameters(self, params):
        """Set PID values
        @param: (float) kp, ki, kd
        """
        self.kp = params.kp
        self.ki = params.ki
        self.kd = params.kd

    #User-defined function
    def calculate_new_goal(self, ir_distances):
        """Determines a new goal for the robot based on which sensors are active"""
        #Normalize the angle values
        
        found = 0
        for dist in ir_distances:
            if dist < 0.18:
                found = 1
                break

        if found == 1:
            angle = 0.0
            weightdist = 0.0
            for i in range(len(ir_distances)):
                weightdist += ir_distances[i]*self.ir_weights[i] 
                angle += self.ir_angles[i]*ir_distances[i]*self.ir_weights[i]

            angle /= weightdist #average distance to the clear
            angle += self.robottheta 
            angle = math.atan2(math.sin(angle), math.cos(angle)) #make correction for pi

            print "Angle: %f\n" % angle
            return angle 

        return self.goaltheta  #default return

    def calculate_new_velocity(self, ir_distances):
        """Adjusts robot velocity based on distance to object"""
        #Compare values to range
        for dist in ir_distances:
            if dist < 0.19:
                return 0.15
        #if nothing found
        return 0.4 

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params

        dt --> supervisor set timestep

        return --> unicycle model list [velocity, omega]"""
        #Select a goal, ccw obstacle avoidance

        self.robotx, self.roboty, self.robottheta = state.pose
        self.goalx, self.goaly = state.goal.x, state.goal.y
        self.goaltheta = math.atan2(self.goaly - self.roboty, self.goalx-self.robotx)

        #If we have reached the goal... stop
        if math.fabs(state.goal.x - self.robotx) < 0.001 and math.fabs(state.goal.y - self.roboty) < 0.001:
            print 'stopping'
            return [0, 0]
    
        #Non-global goal
        theta = self.calculate_new_goal(state.ir_distances) #user defined function
        v_ = self.calculate_new_velocity(state.ir_distances) #user defined function

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
