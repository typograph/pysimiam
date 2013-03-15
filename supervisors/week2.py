"""
(c) PySimiam Team 2013

Contact person: Tim Fuchs <typograph@elec.ru>

This class was implemented for the weekly programming excercises
of the 'Control of Mobile Robots' course by Magnus Egerstedt.
"""
from supervisor import Supervisor
from helpers import Struct
from pose import Pose
from numpy import array, dot
from collections import OrderedDict
from simobject import Path

from math import pi, sin, cos, log1p, sqrt, atan2

class K3Supervisor(Supervisor):
    """The K3Supervisor inherits from the superclass 'supervisor.Supervisor' to implement detailed calculations for any inheriting Khepera3 supervisor. Students are intended to inherit from this class when making their own supervisors. An example of implementation is the :class:`~k3defaultsupervisor.K3DefaultSupervisor` class in which this class is used to reduce noisy code interactions.

Most importantly, the K3Supervisor object implements the system functions necessary to operate a Khepera3, namely the uni2diff unicycle to differential motion model conversion, the Jacobian problem, and any other computationally complex interface.

The UI may use the get_parameters function interface to create docker windows for real-time update of the PID parameters. This is an advanced implementation and is not required for students to properly implement their own supervisors."""
    def __init__(self, robot_pose, robot_info):
        """Initialize internal variables"""
        Supervisor.__init__(self, robot_pose, robot_info)

        # initialize memory registers
        self.prev_left_ticks  = robot_info.wheels.left_ticks
        self.prev_right_ticks = robot_info.wheels.right_ticks

        # Create tracker
        self.tracker = Path(robot_pose, 0)
        
        # Create & set the controller
        self.current = self.create_controller('GoToGoal', self.parameters)
                    
    def init_default_parameters(self):
        """Sets the default PID parameters, goal, and velocity"""
        p = Struct()
        p.goal = Struct()
        p.goal.x = 1.0
        p.goal.y = 1.0
        p.velocity = Struct()
        p.velocity.v = 0.2
        p.gains = Struct()
        p.gains.kp = 10.0
        p.gains.ki = 2.0
        p.gains.kd = 0.0
        
        self.parameters = p
        
    def get_ui_description(self,p = None):
        """Returns the UI description for the docker"""
        if p is None:
            p = self.parameters
        
        return OrderedDict([
                    ('goal', OrderedDict([('x',p.goal.x), ('y',p.goal.y)])),
                    ('velocity', {'v':p.velocity.v}),
                    (('gains',"PID gains"), OrderedDict([
                        (('kp','Proportional gain'), p.gains.kp),
                        (('ki','Integral gain'), p.gains.ki),
                        (('kd','Differential gain'), p.gains.kd)]))])

    def set_parameters(self,params):
        """Set parameters for itself and the controllers"""
        self.parameters.goal = params.goal
        self.parameters.velocity = params.velocity
        self.parameters.gains = params.gains
        self.current.set_parameters(self.parameters)
                                  
    def uni2diff(self,uni):
        """Convert from unicycle model to differential model"""
        (v,w) = uni
        
        #Insert Week 2 Assignment Code Here

        # R = self.robot.wheels.radius
        # L = self.robot.wheels.base_length

        vl = 0
        vr = 0

        #End Week 2 Assignment Code
        
        return (vl,vr)
            
    def get_ir_distances(self):
        """Converts the IR distance readings into a distance in meters"""
        
        #Insert Week 2 Assignment Code Here

        ir_distances = [0]*len(self.robot.ir_sensors.readings) #populate this list

        #End Assignment week2

        return ir_distances

    def estimate_pose(self):
        """Update self.pose_est using odometry"""
        
        #Insert Week 2 Assignment Code Here

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
        
        #End Week 2 Assignment Code
            
        return Pose(x_new, y_new, (theta_new + pi)%(2*pi)-pi)
            
    def execute(self, robot_info, dt):
        """Inherit default supervisor procedures and return unicycle model output (x, y, theta)"""
        output = Supervisor.execute(self, robot_info, dt)
        self.tracker.add_point(self.pose_est)
        return self.uni2diff(output)

    def process(self):
        """Update state parameters for the controllers and self"""
        
        self.parameters.pose = self.pose_est
        return self.parameters
    
    def draw(self, renderer):
        """Draw a circular goal, path and ir_sensors"""
        
        # Draw goal
        renderer.set_pose(Pose(self.parameters.goal.x, self.parameters.goal.y))
        renderer.set_brush(self.robot_color)
        r = self.robot.wheels.base_length/2
        renderer.draw_ellipse(0,0,r,r)
        
        # Draw robot path
        self.tracker.draw(renderer)
        
        # Draw IR distances
        # Calculate vectors:
        crosses = array([ dot(p.get_transformation(), [d,0,1])
                          for d, p in zip(self.get_ir_distances(), self.robot.ir_sensors.poses) ] )
                                
        renderer.set_pen(0)
        for c in crosses:
            x,y,z = c
            
            renderer.push_state()
            renderer.translate(x,y)
            renderer.rotate(atan2(y,x))
        
            renderer.draw_line(0.01,0.01,-0.01,-0.01)
            renderer.draw_line(0.01,-0.01,-0.01,0.01)
            
            renderer.pop_state()                                   
        