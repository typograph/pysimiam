Robots and the world
====================================

Robot
-------------------------------

.. automodule:: robot
    :members:

.. _robot-supervisor-link:

Interaction between the robot and the supervisor
------------------------------------------------

The simulator can run with any robot and any supervisor,
as long as they implement the necessary methods in the :class:`~robot.Robot`
and :class:`~supervisor.Supervisor` base classes.
However, not any supervisor can work with any robot. Specifically,
the supervisor has to correctly use the output of :meth:`robot.Robot.get_info`
and supply the correct input to :meth:`robot.Robot.set_inputs`.

When the simulation is run, the supervisor does not have a direct access to the robot.
All the information that the supervisor can get, is the output of :meth:`~robot.Robot.get_info`.
It is important when implementing a robot to put all the necessary information
about the robot into this structure. This includes the sensor readings and the
geometry of the robot.

The only way that the supervisor can influence the robot, is through
the :meth:`~robot.Robot.set_inputs` method. The supervisor has to produce
the correct output from its :meth:`~supervisor.Supervisor.execute` method.
This output will be fed to the robot at the end of the cycle.

Sensor
-------------------------------
.. automodule:: sensor
    :member-order: bysource
    :members:
