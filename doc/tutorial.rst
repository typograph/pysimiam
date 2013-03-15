Tutorial
========

.. _gui-tutorial:

Using the GUI
-------------

To start the simulator, run the following from the command-line in the ``pysimiam`` folder::
    
    >>> python qtsimiam.py
    
Here is a screenshot of the Qt graphical user interface (GUI) of the simulator:

.. image:: qtsimiam.png

The GUI can be controlled by the menu or the toolbar buttons
(or their equivalent keyboard shortcuts). The first toolbar controls the execution:
    
.. image:: run-buttons.png

The second toolbar controls the display options:
    
.. image:: view-buttons.png

Every time the simulation is restarted, the robot, supervisor and controller code
is reloaded. Therefore, it is possible to change the code without restarting the simulator - 
restarting the simulation is enough.

.. note:: There is a known bug with code reloading malfunctioning. In the case you
 are constantly getting weird error messages, restart the simulator, and they might
 go away.

The docking windows on the left and on the right display the parameters of the
robots' supervisors. These parameters can be changed at runtime by clicking `Apply`.
You can also save and load important parameter sets by using `Save` and `Load` buttons.
It is up to the supervisor to implement those runtime changes.

Implementing your own robot
---------------------------

At the moment only one robot - Khepera3 - is implemented in pySimiam. Most likely,
you will need to customize it for your needs or implement a completely new robot.

A robot from the point of view of the simulator is an drawable object that accepts
control inputs from a supervisor. The pair robot-supervisor is a tightly bound entity,
and the simulator plays only a messenger role between them.

The robot is a SimObject
^^^^^^^^^^^^^^^^^^^^^^^^

Start with subclassing :class:`robot.Robot` and implementing drawing. Two functions
have to be implemented: :meth:`~simobject.SimObject.draw` that draws the robot
on screen and :meth:`~simobject.SimObject.get_envelope` that returns the bounding
rectangle of the robot for collision detection. 

The :meth:`~simobject.SimObject.get_envelope` method should return a list of points describing the polygon. By default this polygon is only used for collision detection,
and so it does not have to correspond exactly to the drawing of the robot.

The :meth:`~simobject.SimObject.draw` method accepts a :class:`~renderer.Renderer`
object as parameter, and can use any of its functions to draw the robot. The drawing
can be as complicated as you wish, or as easy as::

    def draw(self,r):
        """Draw the envelope (shape) filling it with the internal color."""
        r.set_pose(self.get_pose())
        r.set_brush(self.get_color())
        r.draw_polygon(self.get_envelope())

Note the use of :meth:`~renderer.Renderer.set_pose` method. It is much easier
to draw the robot in the robot's internal reference frame, so it is recommended
to use this method before drawing.

If you robot has sensors that can be drawn, an additional method :meth:`~robot.Robot.draw_sensors` can be implemented. We will revisit this point later, when we talk about sensors.

The robot moves
^^^^^^^^^^^^^^^

To move the robot, the simulator calls :meth:`~robot.Robot.move` with the time
interval as a parameter. When implementing this method, you should update
the pose of the robot with :meth:`~simobject.SimObject.set_pose`, sepending on
its internal state.

The internal state of the robot is set by the supervisor passing parameters into :meth:`~robot.Robot.set_inputs`. The format of the parameters is up to the robot
implementation, and the supervisor has to conform to this. Please, provide
sufficient documentation when implementing this method.

Information about the robot
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some of the robot's parameters are important to understand its state. For example,
in case of a differential drive robot, the radius of the wheels and the distance
between them is important. There should be also a way to obtain sensor readings.
This information is expected to be provided by the :meth:`~robot.Robot.get_info`
method. As with :meth:`~robot.Robot.set_inputs`, the actual structure of the
returned object is up to the robot and only matters for the supervisor. You
can turn to the :class:`~robots.khepera3.Khepera3` code for inspiration.

One thing that is important for the simulator, though, is the set of the external
sensors of the robot, as the sensors have to interact with the world. This information
should be returned as a list of sensors from the :meth:`~robot.Robot.get_external_sensors` method.

For example, if your robot has an IR sensor skirt with five sensors, the list
should contain these sensor objects (see :class:`sensor.ProximitySensor`).
You should also implement :meth:`~robot.Robot.draw_sensors` in this case,
which can be as simple as::

    def draw_sensors(self,renderer):
        """Draw the sensors that this robot has"""
        for sensor in self.ir_sensors:
            sensor.draw(renderer)

.. note:: At the moment, the only type of sensors that are supported by the simulator
are proximity sensors, such as ultrasound and IR sensors. Please contact the
developers (or extend the simulator yourself) if you need another kind of external
sensors.

Testing
^^^^^^^

Your robot should be ready now. How can you test it? You need two parts - a :ref:`world<worlds>` and a supervisor (see next section). In the beginning, neither
of the two has to be very complicated. A simple world can just contain one robot,
and your supervisor can work without any controllers. This should be enough to
test the drawing, positioning of the sensors and the dynamics.

Writing a supervisor
--------------------

A supervisor controls a robot. That means, that for a particular kind of robot,
the supervisor can deduce the state of the robot (such as its pose) from the
provided information (such as the reading of its wheel encoders), and set the
inputs (such as wheel speeds) to make the robot attain a particular goal.

In order to achieve this, the supervisor should subdivide achieving the goal
into several small tasks and use one or more controllers to accomplish them.
The controllers are supposed to be general, reusable robot behaviours, and the
task of the supervisor is to choose a suitable controller and supply the expected
parameters to it, as deduced from the particular robot's parameters.

The simple case
^^^^^^^^^^^^^^^

The simplest supervisor only has one behaviour for the robot. In the constructor,
the supervisor should create the corresponding controller and assign it to the :attr:`~supervisor.Supervisor.current` variable. In order to load the controller,
it is recommended to use the :meth:`~supervisor.Supervisor.create_controller` method,
that accepts a controller :ref:`module string<module-string>` and the initial parameters for the controller.

The simulator will call the :meth:`~supervisor.Supervisor.execute` method and
supply the state of the robot, as returned by :meth:`~robot.Robot.robot_info`,
and the elapsed time. By default, the supervisor will use the
:meth:`~supervisor.Supervisor.process` method to interpret the information
about the robot and then use the structure returned by this method to execute
the controller. The return value of the controller is passed to the simulator
and subsequently to the robot's inputs. As the controller output may not be
in the right format for the robot, you can overwrite the :meth:`~supervisor.Supervisor.execute` method and transform the output before
returning it to the simulator (see :meth:`khepera3.K3Supervisor.execute` for an example)

Using the state machine
^^^^^^^^^^^^^^^^^^^^^^^

In a more complicated supervisor, there will be more than one controller, and
thus more than one state. The base supervisor class implements a finite state
machine to handle this. This state machine then switches between
states (controllers) as the state of the robot and its environment changes.

The state machine is defined as a set of controllers (states) and conditions, that would
lead to a change of the current controller. To fully define one state, the :meth:`~supervisor.Supervisor.add_controller` method of the supervisor should
be called in the following way::
    
    self.add_controller(c0, (condition1, c1), (condition2, c2), ...)

to add a state with a controller ``c0``. The conditions are functions that take
no parameters and evaluate to true or false. If a condition evaluates to true,
the controller is switched e.g. to ``c1`` for ``condition1``.

.. note:: Since the condition functions are called without any arguments, all
of the parameters you want to access in them, should be stored in the supervisor.
A good place to do that is the :meth:`~supervisor.Supervisor.process` method,
that is guaranteed to be called before any conditions are checked. In very
complicated cases, that might not be covered by this state machine, you are welcome
to overwrite the :meth:`~supervisor.Supervisor.execute` method and implement
a more fine-grained behaviour.

Run-time access to parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Drawing additional stuff
^^^^^^^^^^^^^^^^^^^^^^^^

Creating a controller
---------------------

