#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

from . import helpers
from .log import log

class Supervisor:
    """
    The supervisor class oversees the control of a single robot.
    The supervisor does not move the robot directly. Instead,
    the supervisor selects a controller to do the work and uses
    the controller outputs to generate the robot inputs.

    :param robot_pose: The initial pose of the robot,
    :type robot_pose: :class:`~pose.Pose`
    :param robot_color: The color of the robot,
    :type robot_color: 0xAARRGGBB or 0xRRGGBB
    :param robot_info: Info structure, the format defined by the robot's
                        :meth:`~robot.Robot.get_info`
    :type robot_info: :class:`~helpers.Struct`

    Any extension of pysimiam will require inheriting from this superclass.
    The important methods that have to be implemented to control a robot
    are
    :meth:`~Supervisor.estimate_pose`,
    :meth:`~Supervisor.get_controller_state`,
    :meth:`~Supervisor.get_ui_description`, and possibly
    :meth:`~Supervisor.process_robot_state`.

    When subclassing this class, an additional keyword parameter `option`
    may be added to the constructor. This parameter of type :class:`~helpers.Struct`
    will be passed in by the simulator in the case that additional parameters are
    specified in the world file.

    The base class implements a state machine for switching between
    different controllers. See :meth:`add_controller` for more
    information.

    .. attribute:: robot

        :type: :class:`~helpers.Struct`

        All the information that the supervisor has about the robot.
        Contains the following fields:

    .. attribute:: robot.initial_pose

        :type: :class:`~pose.Pose`

        The initial pose of the robot, as supplied to the constructor.
        This parameter can be used in the user implementation.

    .. attribute:: robot.pose

        :type: :class:`~pose.Pose`

        The estimated pose of the robot. This variable is updated
        automatically in the beginning of the calculation
        cycle using :py:meth:`~Supervisor.estimate_pose`

    .. attribute:: robot.info

        :type: :class:`~helpers.Struct`

        The robot information structure given by the robot.

    .. attribute:: robot.state

        :type: :class:`~helpers.Struct`

        The current robot state structure given by the robot.

    .. attribute:: robot.color

        :type: int

        The color of the robot in the view (useful for drawing).

    .. attribute:: parameters

        :type: :class:`~helpers.Struct`

        Current parameter structure of the supervisor.
        Updated in :meth:`~Supervisor.set_parameters`

    .. attribute:: current

        :type: :class:`~controller.Controller`

        The current controller to be executed in
        :meth:`~Supervisor.execute`.
        The subclass can set this value in :meth:`~Supervisor.process`
        or in the constructor. In case the state machine is used, the
        current controller will be switched automatically.

    .. attribute:: states

        :type: {:class:`~controller.Controller`:
                [(condition()->bool, :class:`~controller.Controller`)]}

        The transition table of the state machine. The keys of the
        dictionary are the state. The conditions are executed one after
        another until one returns True or the list is through. If one
        of the conditions evaluates to True, its corresponding controller
        is made current, and the evaluation of further conditions is not done.

    """
    
    def __init__(self, robot_pose, robot_color, robot_info):
        
        self.states = {}
        self.current = None

        self.robot = helpers.Struct()
        self.robot.info = robot_info
        self.robot.color = robot_color
        self.robot.pose = robot_pose
        self.robot.initial_pose = robot_pose

    def get_parameters(self):
        """Get the parameter structure of the supervisor.
        A call to ``set_parameters(get_parameters())``
        should not change the supervisor's state

        :return: A supervisor-specific parameter structure.
        :rtype: :class:`~helpers.Struct`
        """
        raise NotImplementedError("Supervisor.get_parameters")

    def set_parameters(self, params):
        """Update this supervisor parameters. The `params` will have
           the same structure as specified by :meth:`get_ui_description`

        :param params: An instance of the paramaters structure as can be
                       returned from :meth:`~Supervisor.get_parameters`.
        :type params: :class:`~helpers.Struct`
        """
        raise NotImplementedError("Supervisor.set_parameters")

    parameters = property(lambda self: self.get_parameters(),
                          lambda self, p: self.set_parameters(p),
                          doc="The parameters that define the state "
                              "of the supervisor")

    def get_ui_description(self):
        """Return a list describing the parameters available to the user.

        :return: A list describing the interface

        The structure returned by this function is used in the interface
        to show a window where the user can adjust the supervisor
        parameters. When the user confirms the changed parameters, this
        structure is used to create the structure that will be passed to
        :meth:`set_parameters`.

        The format of the returned object is as follows:

        - The object is a list of tuples. The order of tuples defines the
          order of fields.
        - The first part of a tuple (key) is either a string or a tuple.
          If it is a tuple, then the first value is the name of the parameter
          field, the second value is an UI label, and the third is an optional
          string identifier if the parameter structure has several fields,
          identical in structure. If the key is a string, it is used both as a
          label, capitalized, and as a field name.
        - The second part of a tuple (value) describes the contents of a UI
          element. It can be either a primitive type, such as an int, a
          bool or a float, in which case it describes one parameter, or
          a (string, list of strings) tuple, for multiple-choice parameters, or
          an object of type :class:`~ui.Parameter`, that allows one to describe
          the interface more precisely. This value can also be a list,
          structured the same way the root list is structured, in which case
          this element contains a subwindow.

        Must be implemented in subclasses.
        """
        raise NotImplementedError("Supervisor.get_ui_description")
    
    ui_description = property(lambda self: self.get_ui_description(),
                              doc="The description of the user interface for "
                                  "setting parameters of this supervisor")

    def create_controller(self, module_string, *parameters):
        """Create and return a controller instance for a given controller
           class.

        :param module_string: a string specifying a class in a module.
                              See :ref:`module-string`
        :type module_string: string
        :param parameters: a parameter structure to be passed to the
                           controller constructor
        :type paramaters: :class:`~helpers.Struct`

        """
        controller_class = helpers.load_by_name(module_string,
                                                'controllers')
        return controller_class(*parameters)

    def get_controller_state(self, controller):
        """Get the parameters that the provided controller needs
        for operation

        :param controller: A controller that will use the parameters
        :type controller: :class:`~controller.Controller`
        :return: A parameter structure in the format appropriate
                 for `controller`.
        :rtype: :class:`~helpers.Struct`

        The result of this function will be used to run the controller.

        Must be implemented in subclasses
        """
        raise NotImplementedError('Supervisor.get_controller_state')

    def process_robot_state(self, robot_state):
        """Evaluate the information about the robot and set state
        variables.
        """
        self.robot.state = robot_state
        self.robot.pose = self.estimate_pose()

    def estimate_pose(self):
        """Updates the pose using odometry calculations.

        :return: The estimated robot pose
        :rtype: :class:`~pose.Pose`

        The result of the evaluation of this function will be used
        to set ``self.robot.pose``

        Must be implemented in subclasses.
        """
        raise NotImplementedError('Supervisor.estimate_pose')
    
    def add_controller(self, controller, *args):
        """Add a transition table for a state with controller

        The arguments are (function, controller) tuples.
        The functions cannot take any arguments.
        Each step, the functions are executed in the order
        they were supplied to this function. If a function
        evaluates to True, the current controller switches to the
        one specified with this function. The target controller
        is restarted using :meth:`controller.Controller.restart`.

        The functions are guaranteed to be called after
        :meth:`process_robot_state`. Thus, :attr:`robot.state`
        should contain actual information about the robot.
        """
        self.states[controller] = args

    def execute(self, robot_state, dt):
        """Based on robot state and elapsed time, return the parameters
        for robot motion.

        :param robot_state: The state of the robot
        :type robot_state: :class:`~helpers.Struct`
        :param float dt: The amount of time elapsed since the last call
                         of `execute`.

        :return: An object (normally a tuple) that will be passed
                 to the robot's :meth:`~robot.Robot.set_inputs` method.

        The default implementation proceeds as follows:

        #. Proccess the state information using :meth:`process_robot_state`
            #. Store the state in :attr:`~Supervisor.robot.state`
            #. Estimate the new robot pose and store it
               in :attr:`~Supervisor.robot.pose`
        #. Switch the controller if instructed by the state machine transitions
        #. Get controller state from
           :meth:`~Supervisor.get_controller_state`
        #. Execute currently selected controller with the parameters from
           previous step
        #. Return the controller output
        """
        self.process_robot_state(robot_state)

        # Switch:
        if self.current in self.states:
            for f, c in self.states[self.current]:
                if f():
                    c.restart()
                    self.current = c
                    log(self, "Switched to {}".format(c.__class__.__name__))
                    break

        #execute the current controller
        return self.current.execute(self.get_controller_state(self.current), dt)

    def draw_background(self, renderer):
        """Draw anything in the view before anything else is drawn (except
        the grid)

        This method is useful for drawing markers that should not obstruct
        the obstacles or the robot, e.g. the goal.
        
        :param renderer: A renderer to draw with
        :type renderer: :class:`~renderer.Renderer`
        """
        pass

    def draw_foreground(self, renderer):
        """Draw anything in the view after everything else is drawn.
        
        This method is useful when it is important to see the estimated
        pose of the robot, e.g. when a vector from robot to goal is drawn.
        This way the robot itself will not obscure the central point.

        :param renderer: A renderer to draw with
        :type renderer: :class:`~renderer.Renderer`
        """
        pass
