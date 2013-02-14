import khepera3

class jonsupervisor(K3Supervisor):
    def __init__(self, robot_pose, robot_info):
        K3Supervisor.__init__(K3Supervisor, robot_pose, robot_info)

        #Add controllers ( go to goal is default)
        self.avoidobstacles = self.add_controller('avoidobstacles.AvoidObstacles', self.ui_params.gains)

    # Decide which controller to use
    def eval_criteria(self):
        self.ui_params.pose = self.pose_est
        self.ui_params.robot_info =   
        return self.ui_params


    def execute(self):
        return 
        


