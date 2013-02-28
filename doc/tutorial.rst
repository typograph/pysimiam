Tutorial
========

Week 1: How to run the program
===============================================
Go to the command line and run::

> python qtsimiam.py

or for those with knowledge of the 'nix OS::

> chmod +x qtsimiam.py
> ./qtsimiam.py

To start the simulation, you have to load a specific environment for the robot,
by selecting `File > Select World.xml File` in the menu, or pressing ``Ctrl+O``
to open the dialog. You can also specify the world name on the command line and
run the program with::

> python qtsimiam.py world.xml

The `play` button starts the simulation. The `rewind` button will reset the robot's
position. If you have changed the supervisor or the controller code, rewinding
will also load your new code.

The simulation view can be adjusted using various buttons on the `View` toolbar.
For example, you can center the view on the robot or hide the robot's trajectory.

Week 2: Unicycle to Differential Transformation
===============================================

Part 1: Unicycle to Differential
--------------------------------

1. Navigate to ``./pysimiam/supervisors/khepera3.py`` and open it in an editor

2. Find the function labeled `uni2diff` in the *khepera3.K3Supervisor* class.

.. code-block:: python

   def uni2diff(uni):
       (v,w) = uni

       #Insert Week 2 Assignment Code Here

       #End Week 2 Assignment Code

       return (vl, vr)

``uni`` is a python tuple with two values. To get those values out of the variable simple apply a statement like this::

   v, w = uni

You are given the values:

- ``w`` (float) - angular velocity :math:`\omega`
- ``v`` (float) - linear velocity :math:`v`
- ``self.robot.wheels.radius`` (float) - :math:`R`, the radius of robot's wheels
- ``self.robot.wheels.base_length`` (float) - :math:`L`, the distance between wheels

Your job is to assign values to ``vl`` and ``vr`` such that the velocity and omega unicycle input correspond to the robot's left and right wheel velocities.

Recall that the equations for unicycle model are:

.. math::
    \frac{dx}{dt} &= v\cos(\phi) \\
    \frac{dy}{dt} &= v\sin(\phi) \\
    \frac{d\phi}{dt} &= \omega

And the differential model is:

.. math::
    \frac{dx}{dt} &= \frac{R}{2}(v_r + v_l)\cos(\phi) \\
    \frac{dy}{dt} &= \frac{R}{2}(v_r + v_l)\sin(\phi) \\
    \frac{d\phi}{dt} &= \frac{R}{L}(v_r - v_l)

Part 2: Odometry 
-----------------------------------------------------------

1. Open ``./pysimiam/supevisors/khepera3.py`` in an editor.

2. Find to the `estimate_pose` function and enter you code in the indicated area. 

You are given these variables:

- ``self.robot.wheels.radius`` (float) - the radius of robot's wheels
- ``self.robot.wheels.base_length`` (float) - the distance between wheels
- ``self.robot.wheels.ticks_per_rev`` (integer) - number of ticks registered per one full wheel revolution
- ``self.robot.wheels.left_ticks`` (integer) - accumulated ticks on the left wheel
- ``self.robot.wheels.right_ticks`` (integer) - accumulated ticks on the right wheel

Note that ``self.robot.wheels.left_ticks`` and ``.right_ticks`` represent
the tick numbering of the encoder and not the elapsed ticks. You will need
to implement a memory variable to store previous values and to calculate
the elapsed ticks. One example of how to do this might be::

   self.prev_right_ticks = self.robot.wheels.right_ticks
   self.prev_left_ticks = self.robot.wheels.left_ticks

Note that ``self.prev_left_ticks`` and ``self.prev_right_ticks`` have to be initialized
in the constructor. The code is already in place for you in the ``__init__()`` method.

Your objective is to solve for the change in `x`, `y`, and `theta`
and from those values update the variables `x_new`, `y_new`, and `theta_new`.
The values `x_new`, `y_new`, and `theta_new` will be used to update
the estimated pose for the supervisor. 

Recall that the equations for odometry are in lecture 2 slides.

Part 3: IR Distance calculation (in meters) 
-----------------------------------------------------------

1. Open ``./pysimiam/supervisors/khepera3.py`` in a text editor.
2. Find the `get_ir_distances` function and insert your code into the indicated area.

You are provided with the variable:

- ``self.robot.ir_sensors.readings`` (list of float) - the readings from Khepera3's IR sensors

Knowing that the sensitive range of distance is 0.02 meters to 0.2 meters and that the intensity as a function of distance is given by:

.. math::
    :nowrap:

    f(\delta) = \left\{\begin{eqnarray}
        3960 & \quad 0m <  \delta  < 0.02m\\ 
        3960e^{-30(\delta-0.02)} & \quad 0.02m <  \delta  < 0.2m
    \end{eqnarray}\right.

Convert to distances for the sensors and assign them to a list called ir_distances. 

For the those curious to explain why IR sensors behave in an exponentially decaying manner: the intensity of the light decays in accordance to the `inverse square law`_. 

.. _inverse square law: http://en.wikipedia.org/wiki/Inverse-square_law

Testing
-----------------------------------------------------------

When you have completed all these exercises, run the simulator with::

> python qtsimiam.py week2.xml

In the beginning, your robot will not move. After you have implemented the
unicycle to differential transformation, it will start to revolve in place.
With the odometry implemented, it will go up by default and crash into the wall.
As soon as the sensors work correctly, you will see it avoid obstacles based
on your calculations.

You can change the goal position in real-time and see the robot move to the new goal.

Week 3: Go To Goal Controller
=============================
1. Open ``./pysimiam/controllers/gotogoal.py`` in an editor.
2. Find the `__init__` and `execute` function in the controller with the appropriate label for week 3.

.. code-block:: python

    def __init__(self, params):
        """init
        @params: 

        """
        Controller.__init__(self,params)
        #Week 3
        #Place any variables you would like to store here
        #You may use this variables for convenience
        self.E = 0 # Integrated error
        self.e_1 = 0 # Previous error calculation

        #End week3

   def execute(self,state,dt):
        """Executes the controller behavior
        @return --> unicycle model list [velocity, omega]
        """
        #Week 3
        # Here is an example of how to get goal position
        # and robot pose data. Feel free to name them differently.

        #x_g, y_g = state.goal.x, state.goal.y
        #x_r, y_r, theta = state.pose

        #Your goal is to modify these two variables
        w = 0
        v = 0 
        #End week3 exercise
        return [v, w] 

Given the following variables:

- ``state.goal.x`` (float) - The X coordinate of the goal
- ``state.goal.y`` (float) - The Y coordinate of the goal
- ``state.pose`` (:class:`~pose.Pose`) - The position and orientation of the robot
- ``state.velocity.v`` (float) - The given target velocity of the simulation, which is usually the maximum available.

To extract the pose data, you can use a command like this::

   (x, y, theta) = state.pose

3. Calculate the bearing (angle) to the goal (``state.goal.x`` and ``state.goal.y``)
4. Calculate the error from the present heading (`theta`) and the bearing.
5. Calculate proportional, integral, and differential terms of the PID.

You are encouraged to reuse your code from week2, but in case you don't want to reuse your code from week2, we placed a default uni2diff and get_ir_distances function within the ``./supervisors/khepera3.py`` module.


Week 4: Avoid Obstacles Controller
==================================
1. Open ``./controllers/avoidobstacles.py`` in an editor.
2. Navigate to the `set_parameters` and `execute` method where the exercise comments begin


.. code-block:: python

        # Week 4 code 
        # These variables will be used to make calculations
        self.angles = params.sensor_angles
        self.weights = [(math.cos(a)+1.1) for a in self.angles]
        # End week 4 code

.. code-block:: python

    def execute(self, state, dt):
        """Executes avoidance behavior based on state and dt. 
        state --> supevisor set ui_params
        dt --> supervisor set timestep
        return --> unicycle model list [velocity, omega]"""

        #Begin week 4 code

        #1. Store the state values for the robot
        self.robotx, self.roboty, self.robottheta = state.pose

        #2. Make calculations for a new goal 
        #3. Calculate proportional error
        #4. Correct for angles (angle may be greater than PI) with atan2
        #5. Calculate integral error
        #6. Calculate differential error
        # store error in self.e_1

        #7. Calculate desired omega
        #Make sure you modify these variables

        v_ = 0
        w_ = 0 
        
        #End week 4 code
        #8. Return solution
        return [v_, w_]



3. Add your code and methods as desired to manipulate ``v_`` and ``w_``.

One suggested idea is to calculate the vector to each point from the robot and weigh them according to the ``self.weight`` variable. Sum the resulting weight and drive the robot to this point.

.. math::
    w = [w_{120}, w_{75}, w_{42}, w_{13}, ...] \\
    r = [r_{120}, r_{75}, r_{42}, ...]^{T} \\
    D = wr 

An alternative method is to weight the angles and use a resultant angle to drive the robot to the desired position. Not that the 180 degree sensor has no opposing sensor to counterweight it.

.. math::
    w = [w_{120}, w_{75}, w_{42}, w_{13}, ...] \\
    d = [d_{120}, d_{75}, d_{42}, ...] \\
    \theta = [\theta_{120}, \theta_{75}, \theta_{42}, ...] \\
    \Theta = \frac{\sum{w_{i}d_{i}\theta_{i}}}{\sum{w_{i}d_{i}}}

