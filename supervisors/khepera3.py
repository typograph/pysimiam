from supervisor import Supervisor
from helpers import Struct
from pose import Pose
from math import pi, sin, cos
from collections import OrderedDict

class K3Supervisor(Supervisor):
    
    def __init__(self, robot_pose, robot_info):
        Supervisor.__init__(self, robot_pose, robot_info)

        self.gtg = self.add_controller('gotogoal.GoToGoal',self.ui_params.gains)
        
        # Default and only controller
        self.current = self.gtg
        
        # initialize memory registers
        self.left_ticks  = robot_info.wheels.left_ticks
        self.right_ticks = robot_info.wheels.right_ticks
                    
    def get_default_parameters(self):
        p = Struct()
        p.goal = Struct()
        p.goal.x = -5.0
        p.goal.y = 5.0
        p.velocity = Struct()
        p.velocity.v = 2.0
        p.gains = Struct()
        p.gains.kp = 1.0
        p.gains.ki = 0.1
        p.gains.kd = 0.0
        return p
        
    def get_ui_description(self,p = None):

        if p is None:
            p = self.ui_params
        
        return { ('pid','GoToGoal'):
                   OrderedDict([
                       ('goal', OrderedDict([('x',p.goal.x), ('y',p.goal.y)])),
                       ('velocity', {'v':p.velocity.v}),
                       ('gains', OrderedDict([
                           (('kp','Proportional gain'), p.gains.kp),
                           (('ki','Integral gain'), p.gains.ki),
                           (('kd','Differential gain'), p.gains.kd)]))])}
                                  
                                    
    def set_parameters(self,params):
        Supervisor.set_parameters(self,params.pid)
            
    def eval_criteria(self):
        # Controller is already selected
        # Parameters are nearly in the right format for go-to-goal
        self.ui_params.pose = self.pose_est
        return self.ui_params
    
    def estimate_pose(self):
        """Update self.pose_est"""
        
        # Get tick updates
        dtl = self.robot.wheels.left_ticks - self.left_ticks
        dtr = self.robot.wheels.right_ticks - self.right_ticks
        
        # Save the wheel encoder ticks for the next estimate
        self.left_ticks += dtl
        self.right_ticks += dtr
        
        x, y, theta = self.pose_est

        R = self.robot.wheels.radius
        L = self.robot.wheels.base_length
        m_per_tick = (2*pi*R)/self.robot.wheels.ticks_per_rev
            
        # distance travelled by left wheel
        dl = dtl*m_per_tick
        # distance travelled by right wheel
        dr = dtr*m_per_tick
            
        theta_dt = (dr-dl)/L
        theta_mid = theta + theta_dt/2
        dst = (dr+dl)/2
        x_dt = dst*cos(theta_mid)
        y_dt = dst*sin(theta_mid)
            
        theta_new = theta + theta_dt
        x_new = x + x_dt
        y_new = y + y_dt                           
           
        return Pose(x_new, y_new, theta_new)
            