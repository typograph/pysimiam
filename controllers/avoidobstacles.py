#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.pid_controller import PIDController
import math
import numpy
from pose import Pose

class AvoidObstacles(PIDController):
    """Avoid obstacles is an example controller that checks the sensors
       for any readings, constructs 'obstacle' vectors and directs the robot
       in the direction of their weighted sum."""
    def __init__(self, params):
        '''Initialize internal variables'''
        PIDController.__init__(self,params)

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.sensor_poses = params.sensor_poses

        # Now we know the poses, it makes sense to also
        # calculate the weights
        #self.weights = [(math.cos(p.theta)+1.5) for p in self.sensor_poses]
        self.weights = [1.0, 1.0, 0.5, 1.0, 1.0]
        
        # Normalizing weights
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""
        
        # Calculate heading:
        x, y = 0, 0
        for d,p,w in zip(state.sensor_distances, self.sensor_poses, self.weights):
            pose = Pose(d) >> p
            x += pose.x*w
            y += pose.y*w
                
        # End Week 4 Assignment
     
        return numpy.array([x, y, 1])
    
    def execute(self, state, dt):
        
        v, w = PIDController.execute(self, state, dt)
        
        # Week 5 code
        #
        
        dmin = min(state.sensor_distances)
        v *= ((dmin - 0.04)/0.26)**2
        
        # 
        
        return v, w    