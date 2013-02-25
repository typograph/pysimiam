from supervisor import Supervisor
from helpers import Struct
from pose import Pose
from math import pi, sin, cos, log1p
from collections import OrderedDict

class K3Supervisor(Supervisor):
    """The K3Supervisor inherits from the superclass 'supervisor.Supervisor' to implement detailed calculations for any inheriting Khepera3 supervisor. Students are intended to inherit from this class when making their own supervisors. An example of implementation is the k3defaultsupervisor.K3DefaultSupervisor class in which this class is used to reduce noisy code interactions.

Most importantly, the K3Supervisor object implements the system functions necessary to operate a Khepera3, namely the uni2diff unicycle to differential motion model conversion, the Jacobian problem, and any other computationally complex interface.

The UI may use the get_parameters function interface to create docker windows for real-time update of the PID parameters. This is an advanced implementation and is not required for students to properly implement their own supervisors."""
    def __init__(self, robot_pose, robot_info):
        Supervisor.__init__(self, robot_pose, robot_info)

        #Create conrollers
        
        # initialize memory registers
        self.left_ticks  = robot_info.wheels.left_ticks
        self.right_ticks = robot_info.wheels.right_ticks
                    
    def get_default_parameters(self):
        """Sets the default PID parameters, goal, and velocity"""
        p = Struct()
        p.goal = Struct()
        p.goal.x = 0.0
        p.goal.y = 0.5
        p.velocity = Struct()
        p.velocity.v = 0.2
        p.gains = Struct()
        p.gains.kp = 10.0
        p.gains.ki = 2.0
        p.gains.kd = 0.0
        return p
        
    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
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

    def get_parameters(self):
        params = Struct()
        params.pid = Supervisor.get_parameters(self)
        return params
                                  
    def set_parameters(self,params):
        Supervisor.set_parameters(self,params.pid)
        self.gtg.set_parameters(params.pid.gains)

    def uni2diff(self,uni):
        """Convert between unicycle model to differential model"""
        (v,w) = uni
        # Assignment Week 2


        # End Assignment
        return (vl,vr)
            
    def get_ir_distances(self):
        """Converts the IR distance readings into a distance in meters"""
        default_value = 3960
        #Assignment week2
        ir_distances = [] #populate this list
        #self.robot.ir_sensors.readings | (may want to use this)


        #End Assignment week2
        return ir_distances

    def process(self):
        """Select controller and insert data into a state info structure for the controller"""
        # Controller is already selected
        # Parameters are nearly in the right format for go-to-goal
        raise NotImplementedError('Supervisor.process') 
    
    def estimate_pose(self):
        """Update self.pose_est using odometry"""
        
        #Week 2 exercise 
        # Get tick updates
        #self.robot.wheels.left_ticks
        #self.robot.wheels.right_ticks
        
        # Save the wheel encoder ticks for the next estimate
        
        #Get the present pose estimate
        x, y, theta = self.pose_est

            
            
        #Use your math to update these variables... 
        theta_new = 0 
        x_new = 0
        y_new = 0
        #end week2 exercise
           
        return Pose(x_new, y_new, (theta_new + pi)%(2*pi)-pi)
            
    def execute(self, robot_info, dt):
        """Inherit default supervisor procedures and return unicycle model output (x, y, theta)"""
        output = Supervisor.execute(self, robot_info, dt)
        return self.uni2diff(output)
