Creating a new GUI
==================

The modular design of pySimiam allows the use of any graphics engine.
Even an HTML implementation should be possible. However, the creation of a new
interface is a complicated task, as it has to support the rendering of the robots,
and the control of supervisor parameters.

At the moment, only a Qt interface is implemented. It can be used as a source of inspiration,
but a new UI does not have to follow exactly the same design. The only requirement is a correct
processing of the simulator messages.

.. todo:: Specify the message types and possible responses.

Subclassing Renderer
--------------------

.. todo:: Describe the Renderer interface

API
---
.. autoclass:: renderer.Renderer
    :noindex:
    :members:
