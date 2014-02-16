#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from controllers.pid_controller import PIDController
from controllers.avoidobstacles import AvoidObstacles
from controllers.gotogoal import GoToGoal

import math
import numpy

class Blending(GoToGoal, AvoidObstacles):
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
        AvoidObstacles.set_parameters(self,params)

    def get_heading_angle(self, state):
        return PIDController.get_heading_angle(self,state)

    def get_heading(self, state):
        """Blend the two heading vectors"""

        # Get the outputs of the two subcontrollers
        u_ao = AvoidObstacles.get_heading(self,state)
        self.away_angle = math.atan2(u_ao[1],u_ao[0])
        u_ao = numpy.array([math.cos(self.away_angle),math.sin(self.away_angle),1])        
        
        self.goal_angle = GoToGoal.get_heading_angle(self,state)
        u_gtg = numpy.array([math.cos(self.goal_angle),math.sin(self.goal_angle),1])        
        
        # Week 5 Assigment Code goes here:
        
        u = u_gtg
        
        # End Week 5 Assigment
                
        return u
    
    def execute(self, state, dt):
        
        v, w = PIDController.execute(self, state, dt)
        
        # Week 5 Assigment Code goes here:
        # End Week 5 Assigment
        
        return v, w    