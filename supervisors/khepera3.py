from supervisor import Supervisor

class K3Supervisor(Supervisor):
    
    def __init__(self, robot, parameters):
        Supervisor.__init__(self,robot,['gotogoal.GoToGoal'], parameters)
        self.set_current(self.controllers['gotogoal'])
            
    def eval_criteria(self):
        #Modify Below Here
        pass
        #Modify Above Here

    def apply_outputs(self,outputs):
        """Apply controller outputs to the robot
        
        To be implemented in subclasses"""
        self.robot.set_unicycle_speeds(outputs)
    
    def estimate_pose(self):
        """Update self.pose_est
        
        To be implemented in subclasses"""
        pass
            