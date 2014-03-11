#
# (c) PySimiam Team 2013
# 
# Contact person: Tim Fuchs <typograph@elec.ru>
#
# This class was implemented for the weekly programming excercises
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisors.week3 import QBGTGSupervisor
from core.simobject import Path
from core.supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class QBGTGSupervisorX(QBGTGSupervisor):
    """QBGTG supervisor uses one go-to-goal controller to make the robot reach the goal."""
    def __init__(self, robot_pose, robot_info):
        """Create the controller"""
        QBGTGSupervisor.__init__(self, robot_pose, robot_info)
        
        # Create the tracker
        self.tracker = Path(robot_pose, 0)

        # Create the controller
        self.gtg = self.create_controller('week3_solved.GoToGoalX', self.parameters)

        # Set the controller
        self.current = self.gtg

    def ensure_w(self,v_lr):
      
        v_l, v_r = v_lr
        
        #Week 3 Assignment Code:
        max_vel = self.robot.wheels.max_velocity
        
        if v_l > v_r:
            tpl_max = (max_vel,-max_vel)
        else:
            tpl_max = (-max_vel,max_vel)
            
        v_lr_max = max(v_l,v_r)
        v_lr_min = min(v_l,v_r)
        
        if v_lr_max > max_vel:
            dvmax = v_lr_max - max_vel
            if v_lr_min - dvmax < -max_vel: # Get maximum omega
                v_l, v_r = tpl_max
            else:
                v_l -= dvmax
                v_r -= dvmax
        elif v_lr_min < -max_vel:
            dvmin = v_lr_min + max_vel # Negative!
            if v_lr_max - dvmin > max_vel: # Get maximum omega
                v_l, v_r = tpl_max
            else:
                v_l -= dvmin
                v_r -= dvmin
        
        #End Week 3 Assigment
        
        return v_l, v_r
