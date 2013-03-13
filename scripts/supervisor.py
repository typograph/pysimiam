# PySimiam Supervisor
import helpers

class Supervisor:
    """
        The supervisor class oversees the control of a single robot.
        The supervisor does not move the robot directly. Instead, the supervisor
        selects a controller to do the work and uses the controller outputs
        to generate the robot inputs.

        :param robot_pose: The initial pose of the robot,
        :type robot_pose: :class:`~pose.Pose`
        :param robot_info: Info structure, the format defined by the robot's
                           :meth:`~robot.Robot.get_info`
        :type robot_info: :class:`~helpers.Struct`
        
        Any extension of pysimiam will require inheriting from this superclass.
        The important methods that have to be implemented to control a robot are
        :meth:`~Supervisor.estimate_pose`, :meth:`~Supervisor.process`,
        :meth:`~Supervisor.get_default_parameters` and :meth:`~Supervisor.get_ui_description`.
        
        The base class implements a state machine for switching between different
        controllers. See :meth:`add_controller` for more information.

        .. attribute:: initial_pose 
            
            :type: :class:`~pose.Pose`
            
            The initial pose of the robot, as supplied to the constructor. This parameter can be used in the user implementation

        .. attribute:: pose_est
        
            :type: :py:class:`~pose.Pose`

            The estimated pose of the robot. This variable is updated automatically in
            the beginning of the calculation cycle using :py:meth:`~Supervisor.estimate_pose`
            
        .. attribute:: ui_params
        
            :type: :class:`~helpers.Struct`

            Current parameter structure of the supervisor. Updated in :meth:`~Supervisor.set_parameters`
            
        .. attribute:: current

            :type: :class:`~controller.Controller`
        
            The current controller to be executed in :py:meth:`~Supervisor.execute`.
            The subclass can set this value in :py:meth:`~Supervisor.process`
            or in the constructor.
            
        .. attribute:: robot
        
            :type: :class:`~helpers.Struct`
        
            The robot information structure given by the robot.

        .. attribute:: robot_color
        
            :type: int
        
            The color of the robot in the view (useful for drawing).
    """
    def __init__(self, robot_pose, robot_info):
        """
        :param robot_pose: The initial pose of the robot,
        :type robot_pose: :class:`~pose.Pose`
        :param robot_info: Info structure, the format defined by the robot
        :type robot_info: :class:`~helpers.Struct`
        """
        self.initial_pose = robot_pose
        self.pose_est = robot_pose
        self.ui_params = self.get_default_parameters()
        self.current = None
        self.robot = None
        self.robot_color = robot_info.color
        
        # Dict controller -> (function, controller)
        self.states = {}

    def get_parameters(self):
        """Get the parameter structure of the supervisor.
        A call to ``supervisor.set_parameters(supervisor.get_parameters())``
        should not change the supervisor's state
        
        :return: A supervisor-specific parameter structure.
        :rtype: :class:`~helpers.Struct`
        """
        return self.ui_params

    def get_default_parameters(self):
        """Return the default parameter structure, suitable for running this supervisor.
        
        Must be implemented in subclasses.
        """
        raise NotImplementedError("Supervisor.get_default_parameters")

    def get_ui_description(self, params = None):
        """Return a dictionary describing the parameters available to the user.

        :param params: An instance of the paramaters structure as returned
                       from get_parameters. If not specified, this method
                       should use :attr:`~Supervisor.ui_params`
        :type params:  :class:`~helpers.Struct`
        
        :return: A dictionary describing the interface
        :rtype: `collections.OrderedDict`
        
        The structure returned by this function is used in the interface
        to show a window where the user can adjust the supervisor parameters.
        When the user confirms the changed parameters, this structure is used
        to create the structure that will be passed to :meth:`set_parameters`.
        
        The format of the returned object is as follows:
        
        - The object is a dictionary. It is recommended to use `collections.OrderedDict`
          for the correct order of fields in the UI form.
        - The key to the dictionary is either a string or a tuple. If it is a tuple,
          then the first value is the name of the parameter field,
          the second value is an UI label, and the third is an optional string
          identifier if the parameter structure has several fields, identical in
          structure. If the key is a string, it is used both as a label, capitalized,
          and as a field name.
        - The values of the dictionary are either floats, in which case they describe
          individual parameters, or dictionaries, structured the same way the root
          dictionary is structured.
        
        Must be implemented in subclasses.
        """
        raise NotImplementedError("Supervisor.get_ui_description")
        
    def set_parameters(self,params):
        """Update this supervisor parameters

        :param params: An instance of the paramaters structure as can be returned
                       from :meth:`~Supervisor.get_parameters`.
        :type params: :class:`~helpers.Struct`
        """
        self.ui_params = params

    def get_controller(self, module_string, parameters):
        """Create and return a controller instance for a given controller class.

        :param module_string: a string specifying a class in a module.
                              See :ref:`module-string`
        :type module_string: string
        :param parameters: a parameter structure to be passed to the controller constructor
        :type paramaters: :class:`~helpers.Struct`

        """
        controller_class = helpers.load_by_name(module_string, 'controllers')
        return controller_class(parameters)
    
    def add_controller(self,controller,*args):
        """Add a transition table for a state with controller
        
           The arguments are (function, controller) tuples.
           The functions cannot take any arguments.
           Each step, the functions are executed in the order
           they were supplied to this function. If a function
           evaluates to True, the current controller switches to the
           one specified with this function. The target controller
           is restarted using :meth:`controller.Controller.restart`.
           
           The functions are guaranteed to be called after :meth:`process`.
           Thus, :attr:`robot` should contain actual information about the robot.
        """
        self.states[controller] = args

    def execute(self, robot_info, dt):
        """Based on robot state and elapsed time, return the parameters
        for robot motion.
        
        :param robot_info: The state of the robot
        :type robot_info: :class:`~helpers.Struct`
        
        :param float dt: The amount of time elapsed since the last call of `execute`.
        
        :return: An object (normally a tuple) that will be passed to the robot's :meth:`~robot.Robot.set_inputs` method.
        
        The default implementation proceeds as follows:
        
        #. Store robot information in :attr:`~Supervisor.robot`
        #. Estimate the new robot pose with odometry and store it in :attr:`~Supervisor.pose_est`
        #. Calculate state variables and get controller parameters from :meth:`~Supervisor.process`
        #. Check if the controller has to be switched
        #. Execute currently selected controller with the parameters from previous step
        #. Return unicycle model parameters as an output (velocity, omega)
        """
        self.robot = robot_info
        self.pose_est = self.estimate_pose()
        params = self.process() #User-defined algorithm
        
        # Switch:
        if self.current in self.states:
            for f, c in self.states[self.current]:
                if f():
                    c.restart()
                    self.current = c
                    print "Switched to {}".format(c.__class__.__name__)
                    break
        
        output = self.current.execute(params,dt) #execute the current controller
        return output

    def draw(self, renderer):
        """Draw anything in the view.
        
        This will be called before anything else is drawn (except the grid)
        
        :param renderer: A renderer to draw with
        :type renderer: :class:`~renderer.Renderer`
        """
        pass

    def process(self):
        """Evaluate the information about the robot and set state variables.
        
        :return: A parameter structure in the format appropriate for the current controller.
        :rtype: :class:`~helpers.Struct`
        
        The result of this function will be used to run the controller.
        
        Must be implemented in subclasses
        """
        raise NotImplementedError('Supervisor.process')
        
    def estimate_pose(self):
        """Updates the pose using odometry calculations.
        
        :return: The estimated robot pose
        :rtype: :class:`~pose.Pose`
        
        The result of the evaluation of this function will be used to set ``self.pose_est``

        Must be implemented in subclasses.
        """
        raise NotImplementedError('Supervisor.estimate_pose')
