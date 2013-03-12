#PySimiam
#Author: John Alexander
#ChangeDate: 8 FEB 2013; 2300EST
#Description: This is the Controller class for PySimiam.
import math

class Controller():
    """
        The controller class defines a behavior for the supervisor class.
        Any implemention must inherit from this class and implement the
        :meth:`~Controller,execute` method to return a unicycle model output.

        :param params: A structure containing the internal controller parameters, such as PID constants.
        :type params: :class:`~helpers.Struct`
        """
    def __init__(self,params):
        """Initialize the controller with parameters
        :params params: A structure containing the internal controller parameters, such as PID constants.
        :type params: :class:`~helpers.Struct`
        """
        self.set_parameters(params)
        self.restart()
    
    def execute(self, state, dt):
        """Given a state and elapsed time, calculate and return robot motion parameters

        :param state: Output from the supervisor :meth:`~Supervisor.process` method
        :type state: :class:`~helpers.Struct`
        :param float dt: Time elapsed since last call to `execute()`
        
        To be implemented in subclasses.
        """
        raise NotImplementedError("Controller.execute")

    def set_parameters(self,params):
        """Set the internal parameters of the controller.
        
        :param params: A structure containing the internal controller parameters, such as PID constants.
        :type params: :class:`~helpers.Struct`

        To be implemented in subclasses,
        """
        raise NotImplementedError("Controller.set_parameters")
    
    def restart(self):
        """Reset the controller to the initial state."""
        pass
