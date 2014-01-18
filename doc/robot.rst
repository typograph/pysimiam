.. _robot-tutorial:

Implementing your own robot
===========================

At the moment only one robot - Khepera3 - is implemented in pySimiam. Most likely,
you will need to customize it for your needs or implement a completely new robot.

A robot from the point of view of the simulator is an drawable object that accepts
control inputs from a supervisor. The pair robot-supervisor is a tightly bound entity,
and the simulator plays only a messenger role between them.

The robot is a SimObject
------------------------

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
to use this method before drawing. It is also recommended to use the color of
the robot :meth:`~robot.Robot.set_pose` during drawing, to be able to distinguish
different robots.

If you robot has sensors that can be drawn, an additional method :meth:`~robot.Robot.draw_sensors` can be implemented. We will revisit this point later, when we talk about sensors.

The robot moves
---------------

To move the robot, the simulator calls :meth:`~robot.Robot.move` with the time
interval as a parameter. When implementing this method, you should update
the pose of the robot with :meth:`~simobject.SimObject.set_pose`, depending on
its internal state.

The internal state of the robot is set by the supervisor passing parameters into :meth:`~robot.Robot.set_inputs`. The format of the parameters is up to the robot
implementation, and the supervisor has to conform to this. Please, provide
sufficient documentation when implementing this method.

Information about the robot
---------------------------

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
-------

Your robot should be ready now. How can you test it? You need two parts - a :ref:`world<world_tutorial>` and a :ref:`supervisor<supervisor-tutorial>` . In the beginning, neither
of the two has to be very complicated. A simple world can just contain one robot,
and your supervisor can work without any controllers. This should be enough to
test the drawing, positioning of the sensors and the dynamics.

API
---

.. automodule:: pose
   :noindex:
   :members:

.. automodule:: simobject
   :noindex:
   :member-order: bysource
   :members:
      
.. automodule:: robot
   :noindex:
   :members:
     
.. automodule:: sensor
   :noindex:
   :member-order: bysource
   :members:


