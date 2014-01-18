XML
====================================

.. include:: world.rst

.. _parameters:
    
Parameter files
---------------

The interface allows users to save the configuration of the supervisor and load
it later. The configuration is saved in XML format with an arbitrary scheme.
The actual format of the file is defined by the supervisor's
:meth:`~supervisor.Supervisor.get_ui_description` method. The returned list of
(key, value) tuples is interpreted as follows:

- Every key in the list is converted either to an XML tag, if the value
    for this key is also a list, or to a tag attribute, if the value
    is a number or a string. The contents of the tags are populated recursively,
    the values of attributes are taken directly from the list.
- The key itself is either a string or a tuple.
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

