#PySimiam
#Author: Tim Fuchs
#Description: A blending controller for coursera
from pid_controller import PIDController
import math
import numpy

class Blending(PIDController):
    """Example of a PID implementation for goal-seek"""
    def __init__(self, params):
        """Create the go-to-goal controlles.
        
        See :meth:`controller.PIDController.set_params`
        for the expected parameter structure
        """
        PIDController.__init__(self,params)
        self.goal_angle = 0
        self.away_angle = 0

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.poses = params.sensor_poses
        self.weights = [1.0]*len(self.poses)
        #self.weights = [(math.cos(p.theta)+1.5) for p in self.poses]
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def get_ao_heading(self,state):
        
        # Calculate vectors:
        self.vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(state.sensor_distances, self.poses) ] )
        
        # Calculate weighted sum:
        heading = numpy.dot(self.vectors.transpose(), self.weights)
        
        mod_heading = math.sqrt(heading[1]**2 + heading[0]**2)
        
        heading[0] /= mod_heading
        heading[1] /= mod_heading
     
        self.away_angle = math.atan2(heading[1],heading[0])
        
        return heading
        

    def get_gtg_heading(self, state):
        """Get the direction from the robot to the goal as a vector."""
        #Calculate the goal position
        x_g, y_g = state.goal.x, state.goal.y
        x_r, y_r, theta = state.pose

        self.goal_angle = math.atan2(y_g - y_r, x_g - x_r) - theta
        # Alternative implementation:
        # return numpy.dot(
        #     numpy.linalg.pinv(state.pose.get_transformation()),
        #     numpy.array([state.goal.x, state.goal.y, 1]))
        
        return numpy.array([math.cos(self.goal_angle),math.sin(self.goal_angle),1])        

    def get_heading(self, state):
        u_ao = self.get_ao_heading(state)
        u_gtg = self.get_gtg_heading(state)
        
        weight_gtg = math.exp(- 0.2 / min(state.sensor_distances) + 1)
        
        u = u_ao*(1-weight_gtg) + u_gtg*weight_gtg
                
        return u
