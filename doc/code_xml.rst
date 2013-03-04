XML
====================================

.. _worlds:
    
World files
-----------

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

.. _parameters:
    
Parameter files
---------------

The interface allows users to save the configuration of the supervisor and load
it later. The configuration is saved in XML format with an arbitrary scheme.
The actual format of the file is defined by the supervisor's
:meth:`~supervisor.Supervisor.get_ui_description` method. The returned dictionary
is interpreted as follows:

- Every key in the dictionary is converted either to an XML tag, if the value
    for this key is also a dictionary, or to a tag attribute, if the value
    is a floating point number. The contents of the tags are populated recursively,
    the values of attributes are taken directly from the dictionary.
- The key to the dictionary is either a string or a tuple.
    - If it is a tuple, then the first element is the name of the XML tag
      (or attribute) and the second element is ignored. If this key translates
      into an XML tag and the tuple has a third element, this one translates
      into the value for an ``id`` attribute of the tag.
    - If the key is a string, it is converted to lower case and used directly
      as a tag or attribute name.



Readers and writers
-------------------

.. automodule:: xmlreader
    :members:

.. automodule:: xmlwriter
    :members:

.. automodule:: xmlobject
    :members:

