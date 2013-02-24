from khepera3 import K3Supervisor
from supervisor import Supervisor

class K3DefaultSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
	self.ui_params.sensor_angles = [pose.theta for pose in robot_info.ir_sensors.poses]
        self.avoidobstacles = self.add_controller('avoidobstacles.AvoidObstacles', self.ui_params)
        self.gtg = self.add_controller('gotogoal.GoToGoal', self.ui_params.gains)

        self.current = self.gtg

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""
        distmin = min(self.get_ir_distances())
        if self.current is self.avoidobstacles:
            print "AVOID"
            if distmin > 0.199:
                self.current = self.gtg

        elif self.current is self.gtg:
            print "GTG"
            if distmin < 0.10:
                self.current = self.avoidobstacles
                self.avoidobstacles.clear_error()


        self.ui_params.pose = self.pose_est
        self.ui_params.sensor_distances = self.get_ir_distances()

        return self.ui_params

    def execute(self, robot_info, dt):
        """Peforms K3Supervisor procedures and converts unicycle output into differential drive output for the Khepera3"""
        output = Supervisor.execute(self, robot_info, dt)
        vl, vr = self.uni2diff(output)
        return (vl, vr) 
