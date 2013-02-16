"""PySimiam
Author: John Alexander
ChangeDate: 8 FEB 2013; 2300EST
Description: This is the Supervisor class for PySimiam.
"""

import helpers

class Supervisor:
    def __init__(self, robot_pose, robot_info):
        self.initial_pose = robot_pose
        self.pose_est = robot_pose
        self.ui_params = self.get_default_parameters()
        self.controller_modules = {}
        self.current = None

    def get_parameters(self):
        """Get parameters of the supervisor.
        
        supervisor.set_parameters(supervisor.get_parameters()) should not change
        the state
        """
        return self.ui_params

    def get_default_parameters(self):
        """Return the default parameter set, suitable for runnig this supervisor
        
        To be implemented in subclasses
        """
        raise NotImplementedError("Supervisor.get_default_parameters")

    def get_ui_description(self, params = None):
        """Return a dictionary, describing the parameters available for the user,
        with the values from params
        
        If params are not specified, use self.ui_params
        
        To be implemented in subclasses
        """
        raise NotImplementedError("Supervisor.get_ui_description")
        
    def set_parameters(self,params):
        self.ui_params = params

    def add_controller(self, module_string, parameters):
        module, controller_class = helpers.load_by_name(module_string, 'controllers')
        self.controller_modules[module_string] = (module, controller_class)
        return controller_class(parameters)

    def get_current(self):
        return self.current

    def execute(self, robot_info, dt):
        """Make decisions about robot motion based on robot_info
        """
        self.robot = robot_info
        self.pose_est = self.estimate_pose()
        params = self.process() #User-defined algorithm
        output = self.current.execute(params,dt) #execute the current controller
        return output

    def process(self):
        """Evaluate the situation and select the right controller. Return the
        right controller params
        to be implemented in subclasses"""
        raise NotImplementedError('Supervisor.process')
        
    def estimate_pose(self):
        """Update self.pose_est
        
        To be implemented in subclasses (different robot drives)"""
        raise NotImplementedError('Supervisor.estimate_pose')
