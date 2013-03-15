"""
(c) PySimiam Team 2013

Contact person: Tim Fuchs <typograph@elec.ru>

This class was implemented for the weekly programming excercises
of the 'Control of Mobile Robots' course by Magnus Egerstedt.
"""from pid_controller import PIDController
import math
import numpy

class Blending(PIDController):
    """A controller blending go-to-goal and avoid-obstacles behaviour"""
    def __init__(self, params):
        """Initialize internal variables"""
        PIDController.__init__(self,params)

        # These two angles are used by the supervisor
        # to debug the controller's behaviour, and contain
        # the headings as returned by the two subcontrollers.
        self.goal_angle = 0
        self.away_angle = 0

    def set_parameters(self, params):
        """Set PID values and sensor poses.
        
        The params structure is expected to have sensor poses in the robot's
        reference frame as ``params.sensor_poses``.
        """
        PIDController.set_parameters(self,params)

        self.poses = params.sensor_poses

        # Now we know the poses, it makes sense to also
        # calculate the weights
        self.weights = [(math.cos(p.theta)+1.5) for p in self.poses]
        
        # Normalizing weights
        ws = sum(self.weights)
        self.weights = [w/ws for w in self.weights]

    def get_ao_heading(self,state):
        """Get the direction away from the obstacles as a vector."""
        
        # Calculate heading:
        
        # 1. Transform distances to vectors in the robot's frame of reference
        self.vectors = \
            numpy.array(
                [numpy.dot(
                    p.get_transformation(),
                    numpy.array([d,0,1])
                    )
                     for d, p in zip(state.sensor_distances, self.poses) ] )
        
        # 2. Calculate weighted sum:
        heading = numpy.dot(self.vectors.transpose(), self.weights)

        # 3. Normalize the heading vector
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
        
        return numpy.array([math.cos(self.goal_angle),
                            math.sin(self.goal_angle),
                            1])

    def get_heading(self, state):
        """Blend the two heading vectors"""

        # Get the outputs of the two subcontrollers
        u_ao = self.get_ao_heading(state)
        u_gtg = self.get_gtg_heading(state)
        
        # Week 5 Assigment Code goes here:
        
        u = u_gtg
        
        # End Week 5 Assigment
                
        return u