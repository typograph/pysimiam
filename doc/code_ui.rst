Graphical Interface
====================================

Drawing
--------

.. autoclass:: renderer.Renderer
    :members:

.. autoclass:: qt_renderer.QtRenderer


UI
---------

.. _ui-sim-queue:
    
Interaction between GUI and the Simulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The interaction between the UI and the simulator happens through
two thread-safe queues. One queue contains the commands for the simulator,
the other queue contains messages from the simulator. The communication
is implemented in the base ui class, `ui.SimUI`.

.. automodule:: ui
    :members:

PyQt4 implementation
^^^^^^^^^^^^^^^^^^^^

.. automodule:: qt_mainwindow
    :members:
        
.. automodule:: qt_paramwindow
    :members:
