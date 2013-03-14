#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: Example PID implementation for goal-seek (incomplete)
from pid_controller import PIDController
import math
import numpy

class FollowWall(PIDController):
    """Follow walls is an example controller that keeps a certain distance
    to the wall and drives alongside it in clockwise or counter-clockwise
    fashion."""
    def __init__(self, params):
        ''' It's just a PID controller'''
        PIDController.__init__(self,params)

        self.vectors = []
        
    def restart(self):
        PIDController.restart(self)
        self.to_wall_vector = None
        self.along_wall_vector = None

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.poses = params.sensor_poses
        self.direction = params.direction
        self.distance = params.distance
        self.sensor_max = params.ir_max

    def get_heading(self, state):
        """Get the direction away from the obstacles as a vector."""
        
        if self.direction == 'left':
            dirfactor = 1
        else:
            dirfactor = -1
        
        # Get the sensors at the good side that also show an obstacle
        sensors = [(p, d) for d, p in zip(state.sensor_distances, self.poses)
                          if 0 < p.theta*dirfactor < math.pi and d < self.sensor_max]

        # Now make sure they are sorted from front to back
        sensors = sorted(sensors, key = lambda (p, d): abs(p.theta))
        
        if len(sensors) == 0:
            return numpy.array([0,0,1])
        
        # Calculate vectors for the sensors 
        self.vectors = numpy.array(
                            [numpy.dot(p.get_transformation(),
                                    numpy.array([d,0,1]))
                             for p, d in sensors] )

        # Now the wall section: (really easy version)
        if len(self.vectors) == 1:
            self.to_wall_vector = self.vectors[0]
            if self.along_wall_vector is None:
                self.along_wall_vector = numpy.array([
                            sensors[0][1]*math.cos(sensors[0][0].theta),
                            sensors[0][1]*math.sin(sensors[0][0].theta),
                            1])

                # Which direction to go?
                # either away from this corner or directly to it.
                # The best way is probably to blend ahead with corner:
                theta_h = sensors[0][0].theta*sensors[0][1]/self.sensor_max
                return numpy.array([
                            sensors[0][1]*math.cos(theta_h),
                            sensors[0][1]*math.sin(theta_h),
                            1])
            else:
                prev_theta = math.atan2(self.along_wall_vector[1],
                                        self.along_wall_vector[0])
                dtheta = prev_theta - sensors[0][0].theta
                if abs(dtheta) > 0.1:
                    dtheta *= 0.1*abs(dtheta)
                
                self.along_wall_vector = numpy.array([
                            sensors[0][1]*math.cos(prev_theta - dtheta),
                            sensors[0][1]*math.sin(prev_theta - dtheta),
                            1])
                                    
                
        else:
            self.along_wall_vector = self.vectors[0] - self.vectors[-1]
            a = self.vectors[-1]
            b = self.along_wall_vector
            dot = numpy.dot
            self.to_wall_vector = a - b*dot(a,b)/dot(b,b)

        weight_steer = math.sqrt(self.to_wall_vector[0]**2
                            + self.to_wall_vector[1]**2) - self.distance
        weight_steer /= self.sensor_max/2
        #print weight_steer
                            
        return self.along_wall_vector + self.to_wall_vector*weight_steer
               