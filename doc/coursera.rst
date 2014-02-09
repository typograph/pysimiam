Using PySimiam in Coursera 'Control of mobile robots' course
************************************************************

Welcome, Coursera students!

Last year, during the first installment of the "Control of Mobile Robots" class,
we have decided to build our own version of the robot simulator that doesn't need
MATLAB. This year we have the exciting opportunity to make our simulator available
to all of the students of the course, thanks to Dr. Magnus Egerstedt and the team.

Our simulator is inspired by the original `Sim.I.Am <http://gritslab.gatech.edu/home/2013/10/sim-i-am/>`_ simulator, and the programming assignments, as well as the robot description
were taken directly from the Sim.I.Am manual by Jean-Pierre de la Croix.
Special thanks to him for his hard work.

Introduction
============

This manual is going to be your resource for using the simulator in the programming exercises for this course. 

Installation
------------

The lastest release of pySimiam for Coursera students is available from `Sourceforge <http://sourceforge.net/projects/pysimiam/files/coursera/>`_ under the name pysimiam-coursera-weekX.zip (where X is the corresponding week for the exercise).

Unzip the latest provided archive and you are good to go!
Run the simulator with::
    
    >>> python qtsimiam_weekX.py

Requirements
^^^^^^^^^^^^

You will need a reasonably modern computer to run the robot simulator. While the simulator will run on hardware older than a Pentium 4, it will probably be a very slow experience. You will also need `Python 2.7 <http://www.python.org/getit/>`_ and two libraries - `Numpy <http://www.scipy.org/Download>`_ for mathematics and `PyQT <http://www.riverbankcomputing.com/software/pyqt/download>`_ for the GUI.

Bug Reporting
^^^^^^^^^^^^^

If you run into a bug (issue) with the simulator, please provide a detailed description either in a message in the discussion forums, in an issue in the sourceforge `issue tracker <http://sourceforge.net/p/pysimiam/tickets/>`_ or in an email to the developers. The bug will get fixed and a new version of the simulator will be available at sourceforge.

Mobile Robot
------------

The mobile robot you will be using in the programming exercises is the QuickBot. The QuickBot is equipped with 5 infrared (IR) range sensors. The QuickBot has a two-wheel differential drive system (two wheels, two motors) with a wheel encoder for each wheel. It is powered by two 4x AA battery packs on top and can be controlled via software on its embedded Linux computer, the BeagleBone Black. You can build the QuickBot yourself by following the hardware lectures in this course.

+-----------------------------------+-------------------------------+
| .. image:: quickbot_simulated.png | .. image:: quickbot-blue.png  |
|    :width: 400px                  |    :width: 400px              |
+-----------------------------------+-------------------------------+   
|   The simulated QuickBot          | The actual QuickBot           |
+-----------------------------------+-------------------------------+   
  
The robot simulator recreates the QuickBot as faithfully as possible. For example, the range, output, and field of view of the simulated IR range sensors match the specifications in the datasheet for the actual Sharp GP2D120XJ00F infrared proximity sensors on the QuickBot.

.. _coursera-irsensors:

IR Range Sensors
^^^^^^^^^^^^^^^^
You will have access to the array of five IR sensors that encompass the QuickBot. The orientation of IR sensors (relative to the body of the QuickBot, as shown in previous figure, is 90°, 45°, 0°, -45° and -90° degrees, respectively. IR range sensors are effective in the range 4 cm to 30 cm only. However, the IR sensors return raw values in the range of [0.4, 2.75]V instead of the measured distances. To complicate matters slightly, the BeagleBone Black digitizes the analog output voltage using a voltage divider and a 12-bit, 1.8V analog-to-digital converter (ADC). The following is a look-up table to demonstrate the relationship between the ADC output, the analog voltage from the IR proximity sensor, and the approximate distance that corresponds to this voltage.

.. csv-table:: 
   :header: "Distance (m)", "Voltage (V)", "ADC out"
   :widths: 12, 12, 12

    0.04 , 2.750 , 917
    0.05 , 2.350 , 783
    0.06 , 2.050 , 683
    0.07 , 1.750 , 583
    0.08 , 1.550 , 517
    0.09 , 1.400 , 467
    0.10 , 1.275 , 425
    0.12 , 1.075 , 358
    0.14 , 0.925 , 308
    0.16 , 0.805 , 268
    0.18 , 0.725 , 242
    0.20 , 0.650 , 217
    0.25 , 0.500 , 167
    0.30 , 0.400 , 133
    
Your supervisor can access the IR array through the ``robot_info`` object that is passed into the ``execute`` function. For example::

    for i, reading in enumerate(robot_info.ir_sensors.readings):
        print 'IR {} has a value of {}'.format(i, reading)

To use the sensor readings, you will have to convert them to actual distances. For that you need to convert from the ADC output to an analog output voltage, and then from the analog output voltage to a distance in meters. The conversion from ADC output to analog output voltage is simply,

.. math::
    :nowrap:

    \begin{equation*}
      V_{\text{ADC}} = \left\lfloor\frac{1000\cdot V_{\text{analog}}}{3}\right\rfloor
    \end{equation*}

Converting from the the analog output voltage to a distance is a little bit more complicated, because a) the relationships between analog output voltage and distance is not linear, and b) the look-up table provides a coarse sample of points.
You can use any way you like to convert between sensor readings and distances. For example, you can use the `SciPy <http://www.scipy.org/Download>`_ mathematical library and interpolate the curve using `scipy.interpolate.inter1d <http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html#scipy-interpolate-interp1d>`_. Or you can fit the provided points with a high-degree polynomial and use this fit.

        
It is important to note that the IR proximity sensor on the actual QuickBot will be influenced by ambient lighting and other sources of interference. For example, under different ambient lighting conditions, the same analog output voltage may correspond to different distances of an object from the IR proximity sensor. The effect of ambient lighting (and other sources of noise) are *not* modelled in the simulator, but will be apparent on the actual hardware.

For the those curious to explain why IR sensors behave in an exponentially decaying manner: the intensity of the light decays in accordance to the `inverse square law`_. 

.. _inverse square law: http://en.wikipedia.org/wiki/Inverse-square_law

.. note:: In general, there is no need to know the exact indexing and number of the sensors, as all the information about the sensors is made available to the controllers and supervisors at runtime. In the best case, your code should be working even if the robot has 9 instead of 5 sensors.

.. _coursera-diffdrivedyn:

Differential Wheel Drive
^^^^^^^^^^^^^^^^^^^^^^^^

.. |vl| replace:: `v`\ :sub:`l`
.. |vr| replace:: `v`\ :sub:`r`

Since the QuickBot has a differential wheel drive (i.e., is not a unicyle), it has to be controlled by specifying the angular velocities of the right and left wheel (|vl|, |vr|), instead of the linear and angular velocities of a unicycle `(v, ω)`. These velocities are computed by a transformation from `(v, ω)` to (|vl|, |vr|). Recall that the dynamics of the unicycle are defined as,

.. math::
    \frac{dx}{dt} &= v\cos(\phi) \\
    \frac{dy}{dt} &= v\sin(\phi) \\
    \frac{d\phi}{dt} &= \omega

The dynamics of the differential drive are defined as,

.. math::
    \frac{dx}{dt} &= \frac{R}{2}(v_r + v_l)\cos(\phi) \\
    \frac{dy}{dt} &= \frac{R}{2}(v_r + v_l)\sin(\phi) \\
    \frac{d\phi}{dt} &= \frac{R}{L}(v_r - v_l)

where `R` is the radius of the wheels and `L` is the distance between the wheels.

The speed for the QuickBot can be obtained in the following way assuming that you have implemented the ``uni2diff`` function, which transforms `(v, ω)` to (|vl|, |vr|)::

    v = 0.15 # m/s
    w = pi/4 # rad/s
    # Transform from v,w to v_r,v_l
    vel_r, vel_l = self.uni2diff(v,w);
    
The angular wheel velocity for the QuickBot is limited to about 80 RPM. It is important to note that if the QuickBot is controlled ot move at maximum linear velocity, it is not possible to achieve any angular velocity, because the angular velocity of the wheel will have been maximized. Therefore, there exists a tradeoff between the linear and angular velocity of the QuickBot: *the faster the robot should turn, the slower it has to move forward*.

Wheel Encoders
^^^^^^^^^^^^^^
Each of the wheels is outfitted with a wheel encoder that increments or decrements a tick counter depending on whether the wheel is moving forward or backwards, respectively. Wheel encoders may be used to infer the relative pose of the robot. This inference is called *odometry*. The relevant information needed for odometry is the radius of the wheel, the distance between the wheels, and the number of ticks per revolution of the wheel. For example::

    R = robot_info.wheels.radius # radius of the wheel
    L = robot_info.wheels.base_length # distance between the wheels
    tpr = robot_info.wheels.ticks_per_rev # ticks per revolution for the wheels

    print 'The right wheel has a tick count of {}'.format(robot_info.wheels.right_ticks)
    print 'The left wheel has a tick count of {}'.format(robot_info.wheels.left_ticks)


Week 1. Getting to know pySimiam
================================

This week's exercises will help you learn about Python and the robot simulator:

1. Since the programming exercises involve programming in Python, you should familiarize yourself with this language. Point your browser to ``http://docs.python.org/2/tutorial/`` to get an introduction to basic concepts.
2. Familiarize yourself with the simulator by reading the section on :ref:`gui-tutorial`, this manual and running the simulator script ``qtsimiam_week1.py``.
  
  * Try different view modes, like focusing on the robot and zooming
  * Change the parameters of the supervisor. For example, change the position of the goal and watch the robot direct itself towards it (to see the position of the goal you have to turn on supervisor info drawing). Also try changing the PID gains.
  * Crash you robot against a wall! The collision detection was not implemented in the supervisor, so the robot does not react to any obstacles and collides with them.
  
3. You are welcome to read the :ref:`API documentation <user-api>` of the simulator parts and look at the simulator's code. The full understanding of the inner working is, however, not required to complete any of the assignments.

Grading
-------

.. image:: submission1.png
    :width: 267px
    :align: left

This week you only need to be able to run the simulator to get full grades. To submit your results for grading, enter your login and password from the `Assignments page <https://class.coursera.org/conrob-002/assignment/list>`_ (these are not your Coursera login and password - those will not work) into the corresponding fields of the grading window (see screenshot), and press the "Test 1: Running the simulator button". The tester will load the *week1* world and wait for the robot to reach the goal (or collide with something). Any submission errors will be displayed in the corresponding field.

If you have closed the submission window, you can call it back by pressing the 'coursera' button in the menu or on the toolbar.

Week 2. Understanding the robot
===============================

In this week's exercises you will teach the supervisor to process the information from the robot.

.. image:: week2_null.png
   :align: left
   :width: 200px

The simulator for this week can be run with::
    
    >>> python qtsimiam_week2.py

Alongside with the robot, some of the information provided by the supervisor is shown. The black dot in the middle of the robot is the current position of the robot, according to the supervisor. The arrow points in the direction of the goal angle (you can set it in supervisor properties). The crosses show the supervisor interpretation of the IR sensor signals. As your robot starts to move, you will also see two trajectories - one being the real trajectory of the robot, and the other calculated by the supervisor.

As you start the simulation for the first time, your robot will not move. To make it move, you will need to implement three components of the QuickBot supervisor, located in ``supervisors/week2.py``. Remember, that it is not necessary to restart the simulator program every time you make change the code. It should suffice to restart the simulation, by pushing the blue double arrow button.

Transformation from unicycle to differential drive dynamics
--------------------------------------------------------------------

The function used by the supervisor to convert from unicycle dynamics `(v, ω)` to differential drive dynamics (left and right *angular* wheel speeds (|vl|, |vr|)) is named ``uni2diff``::

    def uni2diff(self, uni):
        (v,w) = uni

        #Insert Week 2 Assignment Code Here

        # R = self.robot.wheels.radius
        # L = self.robot.wheels.base_length

        vl = 0
        vr = 0

        #End Week 2 Assignment Code

        return (vl, vr)

This function get as its input ``uni``, a python tuple with two values. The function has to return left and right wheel speeds also as a tuple.

You are given the values:

- ``w`` (float) - angular velocity `ω`
- ``v`` (float) - linear velocity `v`
- ``self.robot.wheels.radius`` (float) - `R`, the radius of robot's wheels
- ``self.robot.wheels.base_length`` (float) - `L`, the distance between wheels

You have to set the values:

- ``vl`` (float) - angular velocity of the left wheel |vl|
- ``vr`` (float) - angular velocity of the right wheel |vr|

Your job is to assign values to ``vl`` and ``vr`` such that the velocity and omega unicycle input correspond to the robot's left and right wheel velocities. Please refer to section on :ref:`coursera-diffdrivedyn` for the mathematical formulae.

Testing
^^^^^^^

With the ``uni2diff`` implemented, your robot will start to move as soon as you start the simulation, and as long as you don't change the goal angle, it will move in a circle. If the goal angle is negative, the robot will move clockwise, if positive, counterclockwise, Note, that the supervisor perceives the robot as stanionary (the black dot doesn't move with the robot). To change this, you need to implement odometry.

Odometry
--------
 
Implement odometry for the robot, such that as the robot moves around, its pose `(x, y, θ)` is estimated based on how far each of the wheels have turned. Assume that the robot starts at (0,0,0).
 
The video lectures and, for example the `OrcBoard tutorial <www.orcboard.org/wiki/images/1/1c/OdometryTutorial.pdf>`_, cover how odometry is computed. The general idea behind odometry is to use wheel encoders to measure the distance the wheels have turned over a small period of time, and use this information to approximate the change in pose of the robot.

.. note:: the video lecture may refer to robot's orientation as `ϕ`.

The pose of the robot is composed of its position `(x, y)` and its orientation θ on a 2 dimensional plane. The currently estimated pose is stored in the variable ``self.pose_est``, which bundles ``x``, ``y``, and ``theta`` (θ). The supervisor updates the estimate of its pose by calling the ``estimate_pose`` function. This function is called every ``dt`` seconds, where ``dt`` is 0.02s::

    def estimate_pose(self):
      
        #Insert Week 2 Assignment Code Here

        # Get tick updates
        #self.robot.wheels.left_ticks
        #self.robot.wheels.right_ticks
        
        # Save the wheel encoder ticks for the next estimate
        
        #Get the present pose estimate
        x, y, theta = self.pose_est          
                
        #Use your math to update these variables... 
        theta_new = 0 
        x_new = 0
        y_new = 0
        
        #End Week 2 Assignment Code
            
        return Pose(x_new, y_new, (theta_new + pi)%(2*pi)-pi)

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

Your objective is to solve for the change in `x`, `y`, and `θ`
and from those values update the variables `x_new`, `y_new`, and `theta_new`.
The values `x_new`, `y_new`, and `theta_new` will be used to update
the estimated pose for the supervisor. 

Testing
^^^^^^^

Congratulations! If you have implemented the odometry correctly, the robot moves around and aligns itself to the direction specified as goal angle. If it doesn't, there are several ways  to debug your code. First, it is always possible to insert ``print`` statements anywhere in your program to put some output into the console. Inside the supervisor class, you can also use the ``self.log`` function to output information into the simulator log. Second, you can use the `Python debugger <http://docs.python.org/2/library/pdb.html#module-pdb>`_. Note that the supervisor is running in a separate thread. Third, you can debug your supervisor graphically, by changing its ``draw`` function.

Convertion from raw IR values to distances in meters
----------------------------------------------------

The IR sensors return not the distance in meters, but a `reading`. To retrieve the distances measured by the IR proximity sensor, you will need to implement a conversion from the raw IR values to distances in the ``get_ir_distances`` function::

    def get_ir_distances(self):
        """Converts the IR distance readings into a distance in meters"""
        
        #Insert Week 2 Assignment Code Here

        ir_distances = [0]*len(self.robot.ir_sensors.readings) #populate this list

        #End Assignment week2

        return ir_distances

You are provided with the variable:

- ``self.robot.ir_sensors.readings`` (list of float) - the readings from QuickBot's IR sensors

.. image:: week2_full.png
    :align: left
    :width: 200px

The section on :ref:`coursera-irsensors` contains a table with the values of readings for some sensor-object distances. You should interpolate these values and use you interpolation so that raw values in the range [200, 1375] are converted to distances in the range [0.04, 0.3] m. One simple way to do that is to use your favorite numeric analysis program and to fit the the provided points with a high-degree polynomial. The Numpy library, that you have already installed, can also be used to do the fitting, see the `polynomial module <http://docs.scipy.org/doc/numpy/reference/routines.polynomials.polynomial.html>`_, especially the functions `polyfit` and `polyval`.

After the conversion is implemented, your robot should look like on the image on the left.
 
Testing
^^^^^^^

To test the IR sensor readings, we recommend to open another world file, ``week2ir.xml``, from the simulator window. This world has five robots in it, all of which are close to different walls, and have different sets of IR sensors firing. You should see a black cross at the end of each sensor's cone if you have implemented the conversion for each sensor correctly. In the case the conversion doesn't work as expected, try printing the ``ir_distances`` array at the end of the ``get_ir_distances`` function and watch for errors.

Grading
-------

The three parts are graded separately. For the odometry, an error of 10% of the estimated pose is allowed, due to the low resolution of the encoders.