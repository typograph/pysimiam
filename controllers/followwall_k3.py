#
# (c) PySimiam Team 2013
#
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
import math
import numpy

from core.pose import Pose

from controllers.pid_controller import PIDController

class FollowWall(PIDController):
    """Follow walls is a controller that keeps a certain distance
       to the wall and drives alongside it in clockwise or counter-clockwise
       fashion. Works for Khepera 3 robot.
    """
    def __init__(self, sensor_poses, ir_max):
        '''Initialize internal variables'''
        PIDController.__init__(self)

        self.poses = sensor_poses
        self.sensor_max = ir_max

        # This variable should contain a list of vectors
        # calculated from the relevant sensor readings.
        # It is used by the supervisor to draw & debug
        # the controller's behaviour
        self.vectors = []
        
    def restart(self):
        """Reset internal state"""
        PIDController.restart(self)
        
        # This vector points to the closest point of the wall
        self.to_wall_vector = None
        
        # This vector points along the wall
        self.along_wall_vector = None
        
        # Both vectors are None to enable smoother corner navigation

    def set_parameters(self, direction, distance, ks, v):
        """Set PID values, direction and distance.
        
        :param direction: The direction of wall following
        :type  direction: 'left' or 'right'
        :param distance: The desired distance to the wall to maintain
        :type  distance: float
        :param ks: PID gains
        :type  ks: (kp, ki, kd)
        :param v: Target speed
        :type  v: float
        """
        kp, ki, kd = ks
        PIDController.set_parameters(self, kp, ki, kd, v)

        self.direction = direction
        self.distance = distance

    def get_heading(self, state):
        """Get the direction along the wall as a vector."""
        
        # Factor for sensor selection
        if self.direction == 'left':
            dirfactor = 1
        else:
            dirfactor = -1
        
        # Get the sensors at the good side that also show an obstacle
        sensors = [(p, d) for d, p in zip(state.sensor_distances, self.poses)
                          if 0 < p.theta*dirfactor < math.pi and d < self.sensor_max]

        # Now make sure they are sorted from front to back
        sensors = sorted(sensors, key = lambda (p, d): abs(p.theta))
        
        # No wall - drive a bit to the wall
        if len(sensors) == 0:
            return numpy.array([0.8,dirfactor*0.6,1])
        
        # Calculate vectors for the sensors
        self.vectors = numpy.array(
                            [numpy.dot(p.get_transformation(),
                                    numpy.array([d,0,1]))
                             for p, d in sensors] )

        # Now the wall section: (really easy version)
        if len(self.vectors) == 1: # Corner
            sensor = sensors[0]
            pose = sensor[0]
            reading = sensor[1]
            self.to_wall_vector = self.vectors[0]
            if self.along_wall_vector is None:
                # We've only started, it's a corner,
                # go perpendicular to its vector
                self.along_wall_vector = numpy.array([
                            dirfactor*self.to_wall_vector[1],
                            -dirfactor*self.to_wall_vector[0],
                            1])

                # Which direction to go?
                # either away from this corner or directly to it.
                # let's blend ahead with corner:
                theta_h = pose.theta*reading/self.sensor_max
                return numpy.array([
                            reading*math.cos(theta_h),
                            reading*math.sin(theta_h),
                            1])
            else:
                # To minimize jittering, blend with the previous
                # reading, and don't rotate more than 0.2 rad.
                prev_theta = math.atan2(self.along_wall_vector[1],
                                        self.along_wall_vector[0])
                self.along_wall_vector = numpy.array([
                            dirfactor*self.to_wall_vector[1],
                            -dirfactor*self.to_wall_vector[0],
                            1])
                this_theta = math.atan2(self.along_wall_vector[1],
                                        self.along_wall_vector[0])
                dtheta = prev_theta - this_theta
                if abs(dtheta) > 0.2:
                    dtheta *= 0.2*abs(dtheta)
                
                self.along_wall_vector = numpy.array([
                            reading*math.cos(prev_theta - dtheta),
                            reading*math.sin(prev_theta - dtheta),
                            1])
                                    
                
        else: # More than one vector, approximate with first and last
            self.along_wall_vector = self.vectors[0] - self.vectors[-1]
            a = self.vectors[-1]
            b = self.along_wall_vector
            dot = numpy.dot
            self.to_wall_vector = a - b*dot(a,b)/dot(b,b)

        # Blend along_wall with to_wall depending on the distance
        # if too small, go further away (-to_wall), if too big, go closer
        # (+ to_wall), or go along.
    
        weight_steer = math.sqrt(self.to_wall_vector[0]**2
                            + self.to_wall_vector[1]**2) - self.distance
        weight_steer /= self.sensor_max/2
        
        # Extra weight for driving closer to corners
        if len(self.vectors) == 1:
            weight_steer += 0.3
                           
        return self.along_wall_vector + self.to_wall_vector*weight_steer