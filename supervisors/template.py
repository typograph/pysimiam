from khepera3 import K3Supervisor
from supervisor import Supervisor

class Template(K3Supervisor):
    """The template supervisor implements all required functions to operate a supervisor"""
    def __init__(self, robot_pose, robot_info):
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add at least one controller
        self.gtg = self.add_controller('gotogoal.GoToGoal', self.parameters.gains)

        #Set default controller
        self.current = self.gtg

    def process(self):
        """Sets parameters for supervisors and selects a supervisor
        This code is run every time the supervisor executes"""
        #Add some data to variable self.parameters
        #Below are some default parameters
        #-------------------------------------
        self.parameters.pose = self.pose_est
        self.parameters.ir_readings = self.robot.ir_sensors.readings
        #You may want to convert to distance from readings 
        #using the K3Supervisor methods.
        #-------------------------------------

        #Set the current controller to use
        #self.current = self.gtg # default selection
                

        return self.parameters

    def execute(self, robot_info, dt):
        """K3Supervisor procedures and converts unicycle output into differential drive output for the Khepera3"""
        #You should use this code verbatim
        output = Supervisor.execute(self, robot_info, dt)

        #Convert to differntial model parameters here
        vl, vr = self.uni2diff(output)

        #Return velocities
        return (vl, vr) 
