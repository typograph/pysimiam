# PySimiam Supervisor
import helpers

from supervisor import Supervisor

class Dummy(Supervisor):
    """This supervisor doesn't do anything"""

    def get_parameters(self):
        """Get the parameter structure of the supervisor.
        A call to ``supervisor.set_parameters(supervisor.get_parameters())``
        should not change the supervisor's state
        
        :return: A supervisor-specific parameter structure.
        :rtype: :class:`~helpers.Struct`
        """
        return helpers.Struct()

    def init_default_parameters(self):
        """Populate :attr:`parameters` with default values
        """
        return helpers.Struct()

    def get_ui_description(self, params = None):
        """No parameters"""
        return []
        
    def set_parameters(self,params):
        pass

    def execute(self, robot_info, dt):
        return None

    def get_controller_state(self):
        return None
        
    def estimate_pose(self):
        pass        
