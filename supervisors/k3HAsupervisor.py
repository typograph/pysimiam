from khepera3 import K3Supervisor
from supervisor import Supervisor
from math import sqrt

class K3DefaultSupervisor(K3Supervisor):
    """K3Default supervisor creates two controllers: gotogoal and avoidobstacles. The two behaviors are blended to smooth labyrinth follow"""
    def __init__(self, robot_pose, robot_info):
        """Creates an avoid-obstacle controller and go-to-goal controller"""
        K3Supervisor.__init__(self, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
        self.ui_params.sensor_angles = [pose.theta for pose in robot_info.ir_sensors.poses]
        self.avoid = self.add_controller('avoidobstacles.AvoidObstacles', self.ui_params)
        self.gtg = self.add_controller('gotogoal.GoToGoal', self.ui_params.gains)
        self.hold = self.add_controller('hold.Hold', None)

        #self.hybrid = self.add_controller('hybrid.Hybrid', None)

        self.current = self.gtg

    def set_parameters(self,params):
        K3Supervisor.set_parameters(self,params)
        self.gtg.set_parameters(params.pid.gains)
        self.avoid.set_parameters(self.ui_params)

    def process(self):
        """Selects the best controller based on ir sensor readings
        Updates ui_params.pose and ui_params.ir_readings"""

        #Get the estimated pose
        self.ui_params.pose = self.pose_est
        
        #Get distance from goal, and if @ goal, stop!
        distance_from_goal = sqrt((self.pose_est.x - self.ui_params.goal.x)**2 + (self.pose_est.y - self.ui_params.goal.y)**2)
        if distance_from_goal < self.robot.wheels.base_length/2:
            if not self.current == self.hold:
                self.current = self.hold
        else: #robot is not at goal
            
            #Get ir distances and perform statemachine routines
            self.ui_params.sensor_distances = self.get_ir_distances()
            distmin = min(self.ui_params.sensor_distances)

            #Statemachine!
            if self.current == self.gtg:
                if distmin < self.robot.ir_sensors.rmax*0.35:
                    self.current = self.avoid
    
            elif self.current == self.avoid:
                if distmin > self.robot.ir_sensors.rmax*0.8:
                elif distmin > self.robot.ir_sensors.rmax*0.5 and 
                    distmin <= self.robot.ir_sensors.ramx*0.8: #potential switching surface!!!
                    
            else: #self.current == self.hybrid:
                if distmin > self.robot.ir_sensors.rmax*0.8:
                    self.current = self.gtg


        return self.ui_params
