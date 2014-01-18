Simulator
====================================

.. automodule:: simulator
    :members:

Helper structures
-----------------------

.. _module-string:

Module strings
^^^^^^^^^^^^^^
    
pySimiam loads user code dynamically. This includes robot definitions,
supervisors and controllers. It is important to specify the type of
the robot and its supervisor in the world XML file (see :ref:`world_tutorial`),
and the type of a controller in :meth:`supervisor.Supervisor.add_controller`

The type is specified as a single string with the format ``"mymodule.MyClass"``.
It is equivalent to a python construct ``from mymodule import MyClass``.
If `mymodule` is omitted, like in ``"MyClass"``, the corresponding statement
is ``from myclass import MyClass`` (note the lowercase module name).
If there is more than one point in the string, the class name is taken to
be everything after the last point.

The file `mymodule.py` is expected to reside in the appropriate folder:
`./robots/` for robots, `./controllers/` for controllers and `./supervisors/`
for supervisors.    
    
.. autofunction:: helpers.load_by_name

.. autofunction:: helpers.unload_user_modules

Structures
^^^^^^^^^^

.. autoclass:: helpers.Struct
    :members:

Collision detection
------------------------

.. automodule:: pylygon
    :members:
.. autoclass:: Polygon
    :members:

.. automodule:: rect
    :members:
.. autoclass:: Rect
    :members:

.. automodule:: quadtree
    :members:
.. autoclass:: QuadTree
    :members:
