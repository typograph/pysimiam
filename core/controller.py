#
# (c) PySimiam Team 2014
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

import math

class Controller():
    """The controller class defines a behavior for the supervisor class.
    
       Any implemention must inherit from this class and implement the
       :meth:`~Controller.execute` method to return an appropriate output.
       
       The internal controller parameters can be of two kinds. The first
       kind is for parameters that do not change during the lifetime
       of the controller. These parameters should be passed to the constructor.
       The parameters of second kind may change in the beginning of every cycle.
       Those are passed to the controller by the supervisor before execution
       through :meth:`~Controller.set_parameters`.
    """
    def __init__(self):
        """Initialize the controller. Will call :meth:`~Controller.restart`"""
        self.restart()

    def execute(self, state, dt):
        """Given a state and elapsed time, calculate and return robot
        motion parameters

        :param state: A structure describing the state of the robot,
                      as needed by this controller
        :type state: :class:`~helpers.Struct`
        :param float dt: Time elapsed since last call to `execute()`

        To be implemented in subclasses.
        """
        raise NotImplementedError("Controller.execute")

    def set_parameters(self, *params):
        """Set the internal parameters of the controller.

        :param params: The internal controller
                       parameters, such as PID constants.
        :type params: :class:`~helpers.Struct`

        To be implemented in subclasses,
        """
        if len(params):
            raise NotImplementedError("Controller.set_parameters")

    def restart(self):
        """Reset the controller to the initial state."""
        pass
