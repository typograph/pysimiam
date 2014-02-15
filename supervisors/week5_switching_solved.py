from supervisors.week5_switching import QBSwitchingSupervisor as QBSwitchingSupervisorBase
from supervisor import Supervisor
from math import sqrt, sin, cos, atan2

class QBSwitchingSupervisor(QBSwitchingSupervisorBase):
    """QBDefault supervisor creates two controllers: gotogoal and avoidobstacles. This module is intended to be a template for student supervisor and controller integration"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        QBSwitchingSupervisorBase.__init__(self, robot_pose, robot_info)

        self.states = {}
        
        self.blending = self.create_controller("week5_solved.Blending", self.parameters)

        self.add_controller(self.hold)
        #self.add_controller(self.gtg,
                            #(self.at_goal, self.hold),
                            #(self.at_obstacle, self.avoidobstacles))
        #self.add_controller(self.avoidobstacles,
                            #(self.at_goal, self.hold),
                            #(self.free, self.gtg),
                            #)
        self.add_controller(self.gtg,
                            (self.at_goal, self.hold),
                            (self.unsafe, self.blending))
        self.add_controller(self.avoidobstacles,
                            (self.at_goal, self.hold),
                            (self.free, self.gtg),
                            (self.safe, self.blending)                            
                            )
        self.add_controller(self.blending,
                            (self.at_goal, self.hold),
                            (self.free, self.gtg),
                            (self.at_obstacle, self.avoidobstacles),
                            )

    def set_parameters(self,params):
        QBSwitchingSupervisorBase.set_parameters(self,params)
        self.blending.set_parameters(self.parameters)

    def at_goal(self):
        return self.distance_from_goal < self.robot.wheels.base_length/2
        
    def at_obstacle(self):
        return self.distmin < self.robot.ir_sensors.rmax/2
        
    def unsafe(self):
        return self.distmin < self.robot.ir_sensors.rmax/1.5
        
    def safe(self):
        return self.distmin > self.robot.ir_sensors.rmax/1.2

    def free(self):
        return self.distmin > self.robot.ir_sensors.rmax/1.1

    def process_state_info(self, state):
        """Selects the best controller based on ir sensor readings
        Updates parameters.pose and parameters.ir_readings"""

        QBSwitchingSupervisorBase.process_state_info(self,state)

        self.distance_from_goal = sqrt((self.pose_est.x - self.parameters.goal.x)**2 + (self.pose_est.y - self.parameters.goal.y)**2)
        self.distmin = min(self.parameters.sensor_distances)        