#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: This is the Supervisor class for PySimiam.
import helpers

class Supervisor:
    """The supervisor class creates a superclass for interfacing with robot objects. Any extension of pysimiam will require inheriting from this superclass."""
    def __init__(self, robot_pose, robot_info):
        """
        @param:     robot_pose - Pose object
                    robot_info - Info structure
        """
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
        return controller_class(parameters)

    def get_current(self):
        """Get current controller
        @return controller object
        """
        return self.current

    def execute(self, robot_info, dt):
        """Default execution procedures
        1. Get robot information
        2. Estimate pose with odometry
        3. Update paramaters with the supervisor process (also select controller)
        4. Execute currently selected controller behavior
        5. Return unicycle model as an output (velocity, omega)
        Make decisions about robot motion based on robot_info
        """
        self.robot = robot_info
        self.pose_est = self.estimate_pose()
        params = self.process() #User-defined algorithm
        output = self.current.execute(params,dt) #execute the current controller
        return output

    def process(self):
        """Evaluate the sensors and select a controller
        Update parameters to by passed to the controller
        Must be implemented in subclasses
        """
        raise NotImplementedError('Supervisor.process')
        
    def estimate_pose(self):
        """Updates the pose using odometry calculations
        Update self.pose_est variable
        Must bed implemented in subclasses (different robot drives)
        """
        raise NotImplementedError('Supervisor.estimate_pose')
