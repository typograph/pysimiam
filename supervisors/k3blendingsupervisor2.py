from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt

class K3BlendingSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
        self.ui_params.sensor_angles = [pose.theta for pose in robot_info.ir_sensors.poses]
        self.ui_params.sensor_max = robot_info.ir_sensors.rmax
        self.blending = self.add_controller('blending.BlendGTGAvoid', self.ui_params)
        self.hold = self.add_controller('hold.Hold', None)

        self.current = self.blending

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.blending.set_parameters(self.ui_params)

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        self.ui_params.pose = self.pose_est

        distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        if distance_from_goal < self.robot.wheels.base_length/2:
            if not self.current == self.hold:
                print "GOAL"
                self.current = self.hold
        else:
            self.ui_params.sensor_distances = self.get_ir_distances()
            if self.current != self.blending:
                self.current = self.blending

        return self.ui_params
