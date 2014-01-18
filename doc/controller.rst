.. _controller-tutorial:

Creating a controller
=====================

A controller represents a specific robotic behavior. Its main method is
:meth:`~controller.Controller.execute`, that accepts the state of the robot and
the elapsed time as arguments and returns a structure suitable for controlling
the robot. For example, the controllers implemented in pySimiam so far
return a `(v, ω)` tuple  - the linear and angular speeds in the unicycle model.

The controller can also have a set of parameters, set with :meth:`~controller.Controller.set_parameters`.
Again, the structure of the parameters is up to the controller implementation.
The supervisor using this controller should provide suitable arguments
to the controller's constructor.

Additionally, the controller should provide the means to reset its internal state
by implementing :meth:`~controller.Controller.restart`. This method is called
every time the supervisor switches from one controller to the next, and it might
be necessary to reset the accumulated error, for example, as in a PID controller.

API
---

.. automodule:: controller
    :noindex:
    :members:
