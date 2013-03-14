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

Writing a supervisor
--------------------

The simple case
^^^^^^^^^^^^^^^

Using the state machine
^^^^^^^^^^^^^^^^^^^^^^^

Drawing additional stuff
^^^^^^^^^^^^^^^^^^^^^^^^

Creating a controller
---------------------

