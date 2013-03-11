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
        self.away_angle = 0
        self.vectors = []

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

        self.poses = params.sensor_poses
        self.weights = [1.0]*len(self.poses)
        #self.weights = [(math.cos(p.theta)+1.5) for p in self.poses]
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def calculate(self, state):
        # Calculate vectors:
        self.vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(state.sensor_distances, self.poses) ] )
        
        # Calculate weighted sum:
        heading = \
            numpy.dot( \
                numpy.dot(state.pose.get_transformation(),self.vectors.transpose()),
                self.weights)
     
        rx, ry, rt = state.pose
        theta = math.atan2(heading[1]-ry,heading[0]-rx)
        self.away_angle = theta - rt
    
    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params

        dt --> supervisor set timestep

        return --> unicycle model list [velocity, omega]"""
     
        self.calculate(state)
        v_ = state.velocity.v

        #1. Calculate simple proportional error
        error = self.away_angle

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
