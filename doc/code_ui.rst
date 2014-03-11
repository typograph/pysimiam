Graphical Interface
====================================

Drawing
--------

.. autoclass:: core.renderer.Renderer
    :members:

.. autoclass:: gui.qt_renderer.QtRenderer

.. autoclass:: gui.wx_renderer.wxGCRenderer


UI
---------

.. _ui-sim-queue:
    
Interaction between GUI and the Simulator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The interaction between the UI and the simulator happens through
two thread-safe queues. One queue contains the commands for the simulator,
the other queue contains messages from the simulator. The communication
is implemented in the base ui class, `ui.SimUI`.

.. automodule:: core.ui
    :members:

PyQt4 implementation
^^^^^^^^^^^^^^^^^^^^

.. automodule:: gui.qt_mainwindow
    :members:
        
.. automodule:: gui.qt_paramwindow
    :members:

wxPython implementation
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: gui.wx_mainwindow
    :members:
