.. _world_tutorial:

World files
-----------

The simulator places robots in an environment (world) with obstacles. You can create
your own environments or modify the existing ones. The world XML files reside in the
"worlds" subfolder of the pySimiam distribution.

Creating new worlds
^^^^^^^^^^^^^^^^^^^

Although worlds can be written by hand (see next section), it might be more pleasant to create a world
in a vector graphics editor. A tool named ``svg2world`` is provided with pySimiam
to convert SVG [#svgformat]_ files to world files.

``svg2world`` only supports a subset of svg, notably all the groups except
the top one are ignored. Only the contents of this top group are processed
(in Inkscape, the top group is the default layer).

A path with 1 or 2 points is interpreted as a robot, with the position of the robot
determined by the first point, and the direction by the second one. An optional
attribute *robot* defines the robot class and *supervisor* defines the associated
supervisor.

The rectangles and the paths with more than 2 points will be converted to obstacles,
unless their 'id' attribute begins with 'marker', such as 'marker345'. A robot will
collide with obstacles, but will ignore markers.

The color of obstacles, markers and robots is taken directly from the fill color.
The stroke color is ignored.

Run the tool with

  >>> python tools/svg2world.py your_drawing.svg worlds/your_world.xml


File format
^^^^^^^^^^^

The world for the simulation is specified in an XML file. This file
contains the position and shape of all obstacles and markers, as well
as the position, class and supervisor class of all robots.

An obstacle is a polygon, that the robot can collide with.
It can be detected by proximity sensors. An ``obstacle`` tag has to contain
a pose and a list of points (minimum three points).
This example specifies a triangular obstacle:

.. code-block:: xml

    <obstacle>
        <pose x="0" y="0" theta="0" />
        <geometry>
            <point x="0" y="0" />
            <point x="0.3" y="0.3" />
            <point x="-0.3" y="0.3" />
        </geometry>
    </obstacle>

A marker is like an obstacle that the robot can go through. It can not
influence the robot in any way, and will not be detected by proximity sensors.
The required fields are the same as in the case of an obstacle. Here is an
example of a rotated square marker:

.. code-block:: xml

    <marker>
        <pose x="0" y="-1.3" theta="1.57" />
        <geometry>
            <point x="0" y="0" />
            <point x="0" y="0.3" />
            <point x="0.3" y="0.3" />
            <point x="0.3" y="0" />
        </geometry>
    </marker>

Each ``robot`` tag in the world represents a robot. It has to contain the robot pose,
class and the supervisor class (see :ref:`module-string`).

.. code-block:: xml

    <robot type="Khepera3">
        <supervisor type="K3DefaultSupervisor" />
        <pose x="1" y="0" theta="-1.57" />
    </robot>

All objects can also have a ``color`` attribute in the form ``#rrggbb``.
The objects have to be wrapped in a ``simulation`` tag. The DTD for the world
XML reads:

.. code-block:: dtd

    <!ELEMENT simulation (robot+,obstacle*,marker*)>

    <!ELEMENT robot (supervisor,pose)>
    <!ATTLIST robot type CDATA #REQUIRED
                    color CDATA #IMPLIED>
                    
    <!ELEMENT obstacle (pose, geometry)>
    <!ATTLIST obstacle color CDATA #IMPLIED>
    
    <!ELEMENT marker (pose, geometry)>
    <!ATTLIST marker color CDATA #IMPLIED>
    
    <!ELEMENT pose EMPTY>
    <!ATTLIST pose x CDATA #REQUIRED
                   y CDATA #REQUIRED
                   theta CDATA #REQUIRED>
                   
    <!ELEMENT geometry (point, point+)>
    <!ELEMENT point EMPTY>
    <!ATTLIST point x CDATA #REQUIRED
                    y CDATA #REQUIRED>

.. [#svgformat] `Scalable Vector Graphics <http://en.wikipedia.org/wiki/Scalable_Vector_Graphics>`_ is a widely used format. SVG files can be created with e.g. `Inkscape <www.inkscape.org>`_