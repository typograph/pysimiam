#
# (c) PySimiam Team 2014
#
# Contact person: John Witten <jon.witten@gmail.com>
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#
from supervisor import Supervisor
from helpers import Struct
from pose import Pose
from math import pi, sin, cos, log1p
from simobject import Path

class QuickBotSupervisor(Supervisor):
    """The QuickBotSupervisor inherits from the superclass 'supervisor.Supervisor'
       to implement detailed calculations for any inheriting QuickBot supervisor.
       Students are intended to inherit from this class when making their own supervisors.
       An example of implementation is the :class:`~quickbotdefaultsupervisor.QuickBotDefaultSupervisor` class
       in which this class is used to reduce noisy code interactions.

       Most importantly, the QuickBotSupervisor object implements the system functions
       necessary to operate a QuickBot, namely the uni2diff unicycle to differential
       motion model conversion, the Jacobian problem, and any other computationally complex interface.

       The UI may use the get_parameters function interface to create docker windows
       for real-time update of the PID parameters. This is an advanced implementation
       and is not required for students to properly implement their own supervisors."""
    def __init__(self, robot_pose, robot_info):
        """Initialize internal variables"""
        Supervisor.__init__(self, robot_pose, robot_info)

        # initialize memory registers
        self.left_ticks  = robot_info.wheels.left_ticks
        self.right_ticks = robot_info.wheels.right_ticks
        
        # Let's say the robot is that big:
        self.robot_size = robot_info.wheels.base_length
        
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
        
        return [('goal', [('x',p.goal.x), ('y',p.goal.y)]),
                ('velocity', [('v',p.velocity.v)]),
                (('gains',"PID gains"), [
                    (('kp','Proportional gain'), p.gains.kp),
                    (('ki','Integral gain'), p.gains.ki),
                    (('kd','Differential gain'), p.gains.kd)])]

    def set_parameters(self,params):
        """Set param structure from docker"""
        self.parameters.goal = params.goal
        self.parameters.velocity = params.velocity
        self.parameters.gains = params.gains
                                  
    def uni2diff(self,uni):
        """Convert between unicycle model to differential model"""
        (v,w) = uni

        summ = 2*v/self.robot.wheels.radius
        diff = self.robot.wheels.base_length*w/self.robot.wheels.radius

        vl = (summ-diff)/2
        vr = (summ+diff)/2

        return (vl,vr)
            
    def get_ir_distances(self):
        """Converts the IR distance readings into a distance in meters"""
        
        ir_distances = [ \
                            6.9102954665694e-01 \
                          - 3.1412389062494e-03 *reading \
                          + 7.9044887227795e-06 *reading**2 \
                          - 1.1785219658536e-08 *reading**3 \
                          + 1.0253386689857e-11 *reading**4 \
                          - 4.7767484008798e-15 *reading**5 \
                          + 9.1559082598082e-19 *reading**6 \
            for reading in self.robot.ir_sensors.readings ]

        return ir_distances
    
    def estimate_pose(self):
        """Update self.pose_est using odometry"""
        
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
           
        return Pose(x_new, y_new, (theta_new + pi)%(2*pi)-pi)

    def get_controller_state(self):
        return self.parameters
            
    def execute(self, robot_info, dt):
        """Inherit default supervisor procedures and return unicycle model output (x, y, theta)"""
        output = Supervisor.execute(self, robot_info, dt)
        return self.uni2diff(output)

    def draw(self, renderer):
        """Draw a circular goal"""
        renderer.set_pose(Pose(self.parameters.goal.x, self.parameters.goal.y))
        renderer.set_brush(self.robot_color)
        r = self.robot_size/2
        renderer.draw_ellipse(0,0,r,r)