# -*- coding: utf-8 -*-

import sys
import json
import re


class Struct:
    """This class describes structures with arbitrary fields.
       It is used, e.g. for the communication between the supervisor
       and the UI.

       Example::

            p = Struct()
            p.goal = Struct()
            p.goal.x = 0.0
            p.goal.y = 0.5
            p.velocity = Struct()
            p.velocity.v = 0.2
            p.gains = Struct()
            p.gains.kp = 10.0
            p.gains.ki = 2.0
            p.gains.kd = 0.0

       Alternatives::

            p = Struct({'goal':{'x':0.0, 'y':0.5}, 'velocity':{'v':0.2}, 'gains':{'kp':10.0, 'ki':2.0, 'kd':0.0}})
            p = Struct("{'goal':{'x':0.0, 'y':0.5}, 'velocity':{'v':0.2}, 'gains':{'kp':10.0, 'ki':2.0, 'kd':0.0}}")

       In the second case, the string has to be a valid JSON object.
       It is also impossible to use dictionaries as values in the Struct
       in these cases - they will be converted to Struct automatically.

       ::note The fields of a Struct must be valid Python identifiers,
       and cannot be Python keywords, such as 'class' or 'for'.
       In order to increase portability between Python 2 and 3,
       only ASCII letters, digits and '_' are allowed in the field names.

    """

    __identifier = re.compile(r"^[_A-Za-z][_a-zA-Z0-9]*$")

    @classmethod
    def is_valid_field_name(cls, name):
        if not isinstance(name, str):
            if sys.version_info.major == 3 or not isinstance(name, unicode): 
                return False
        from keyword import iskeyword
        if iskeyword(name):
            return False
# We cannot allow Unicode identifiers, as those will not work
# in python 2. If Unicode identifiers are desirable,
# uncomment the following line (this will not work for py2)
#       return name.isidentifier()
        return cls.__identifier.match(name) is not None

    def __init__(self, desc=None):
        if desc is not None:
            try:
                dct = dict(desc)
            except Exception:
                try:
                    dct = dict(json.loads(desc))
                except Exception:
                    raise ValueError("Invalid Struct description {}".format(
                                     repr(desc)))

            for k, v in dct.items():
                if not Struct.is_valid_field_name(k):
                    raise ValueError("Invalid Struct field name {}".format(k))
                if isinstance(v, dict):
                    self.__dict__[k] = Struct(v)
                else:
                    self.__dict__[k] = v

    def __len__(self):
        nleaves = 0
        for v in self.__dict__.values():
            if isinstance(v, Struct):
                nleaves += len(v)
            else:
                nleaves += 1
        return nleaves

    def __str__(self):
        def str_field(key, value):
            indent = " "*(len(str(key)) + 3)
            str_value = str(value)
            if isinstance(value, Struct):
                # create indent
                str_value = str_value.replace('\n', '\n'+indent)
            return "{}: {}".format(key, str_value)

        return "Struct\n {}".format("\n ".join((str_field(k, v)
                                    for k, v in self.__dict__.items())))

    def __contains__(self, item):
        return item in self.__dict__

    def __getitem__(self, key):
        if not Struct.is_valid_field_name(key):
            raise IndexError("Invalid Struct field name {}".format(key))
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if not Struct.is_valid_field_name(key):
            raise ValueError("Invalid Struct field name {}".format(key))
        self.__dict__[key] = value

    def __delitem__(self, key):
        if not Struct.is_valid_field_name(key):
            raise ValueError("Invalid Struct field name {}".format(key))
        del self.__dict__[key]

    def __repr__(self):
        # This might be the same as repr(dict), but it's safer.
        return json.dumps(self.__dict__, default=lambda x: x.__dict__)

    def __eq__(self, other):
        if not isinstance(other, Struct):
            return NotImplemented

        return (len(self.__dict__) == len(other.__dict__) and
                all(k in other.__dict__ and
                    other.__dict__[k] == v for k, v in self.__dict__.items()))

    def __lshift__(self, other):
        """Create a Struct with values from this Struct updated with values
           from *other*.
           The values only get updated if they are of the same type.
           A tuple `(updated, ignored)` is returned, specifying the number
           of fields updated from *other* and the number of fields of *other*
           ignored as not corresponding to this structure.
        """
        news = Struct(repr(self))
        news <<= other
        return news

    def __ilshift__(self, other):
        """Updates this Struct with values from *other*.
           The values only get updated if they are of the same type. The only
           exception is that integer numbers will update floating-point numbers
           but not the other way around.
           A tuple `(updated, ignored)` is returned, specifying the number
           of fields updated from *other* and the number of fields of *other*
           ignored as not corresponding to this structure.
        """
        update_struct(self, other)
        return self


def update_struct(s, other, lazy=True):
    """Calling this function is equivalent to calling ``s <<= other``.
       In addition to updating the structure, this function also returns
       the number of updated fields in *s* and the number of ignored fields
       in *other*. If *lazy* is False, ValueError will be raised if the number
       of ignored fields is not zero, or if some types do not match.
    """
    if not isinstance(other, Struct):
        return NotImplemented
    updated = 0
    ignored = 0
    for k in other.__dict__:
        if k not in s.__dict__:
            if lazy:
                ignored += isinstance(other.__dict__[k], Struct) \
                           and len(other.__dict__[k]) \
                           or 1
            else:
                raise ValueError("Extra field {}".format(k))
        elif isinstance(s.__dict__[k], float) and \
             isinstance(other.__dict__[k], int) and \
             not isinstance(other.__dict__[k], bool):
            s.__dict__[k] = float(other.__dict__[k])
            updated += 1
        elif not isinstance(s.__dict__[k], type(other.__dict__[k])) or \
             not isinstance(other.__dict__[k], type(s.__dict__[k])):
            if not lazy:
                raise ValueError("Type mismatch on field {}: {} is not {}".\
                    format(k,
                           other.__dict__[k].__class__.__name__,
                           s.__dict__[k].__class__.__name__))
        elif isinstance(s.__dict__[k], Struct):
            u, i = update_struct(s.__dict__[k], other.__dict__[k], lazy)
            updated += u
            ignored += i
        else:
            s.__dict__[k] = other.__dict__[k]
            updated += 1

    return updated, ignored


def struct_from_XML(xml, lazy=False, root=None):
    """Returns a Struct corresponding to XML structure in *xml*.
       The root tag of the XML is treated as root Struct.
       Every attribute of the tag is converted to a field in the structure.
       Type conversion from string to `bool`, `int` and `float`
       will be attempted.
       Every child tag  is converted to a field of type Struct, except for
       cases when the tag contains no attributes, but has content. In such
       cases the content is imported as a field of passable type, generally
       `str`, if it cannot be converted to `int` or `float`.

       note:: XML is not a good format for saving Struct. For example,
       in XML a tag can (even should) contain a lot of same-named child tags,
       which is not allows in Struct. Also attribute types cannot be determined
       easily. At best, Struct describes only a subset of XML, but e.g. lists
       are not easily representable in XML. We recommend using JSON for saving
       and loading Struct.

       The *lazy* parameter controls the behaviour on XML elements that cannot
       be imported, such as multiple identical child tags. With ``lazy==False``,
       those raise ValueError, with ``lazy==True`` they are ignored.
    """
    def populate(s, x):
        """x is a tag of type xml.etree.ElementTree.Element, s is a Struct"""
        # Process attributes
        for k in x.attrib:
            # Type coersion
            value = x.attrib[k]
            if isinstance(value, str) or \
               (sys.version_info.major == 2 and isinstance(value, unicode)):
                try:
                    s[k] = int(value)
                except ValueError:
                    try:
                        s[k] = float(value)
                    except ValueError:
                        if value == 'false':
                            s[k] = False
                        elif value == 'true':
                            s[k] = True
                        else:
                            s[k] = value
            else:
                s[k] = x.attrib[k]

        # Process children
        for t in x:
            if t.tag in s:
                if not lazy:
                    raise ValueError(
                        "Duplicate child {} in tag {}".format(
                            t.tag,
                            x.tag))
            elif t.text and len(t) == 0:
                if t.attrib:
                    if lazy:
                        raise ValueError(
                            "Tag {} contains both attributes and content".
                            format(t.tag))
                    else:
                        s[t.tag] = Struct()
                        populate(s[t.tag], t)
                else:
                    try:
                        s[t.tag] = int(t.text)
                    except ValueError:
                        try:
                            s[t.tag] = float(t.text)
                        except ValueError:
                            s[t.tag] = t.text
            else:
                s[t.tag] = Struct()
                populate(s[t.tag], t)

    import xml.etree.ElementTree as ET
    s = Struct()
    tree_root = ET.fromstring(xml)
    if root is not None and tree_root.tag != root:
        raise ValueError("Root tag is {}, not {}".format(tree_root.tag, root))
    populate(s, tree_root)
    return s


def struct_volume(s):
    """This function returns complete number of fields in Struct,
       including fields of type Struct and their content
    """
    n = 0
    for k in s.__dict__:
        n += 1
        if isinstance(s[k], Struct):
            n += struct_volume(s[k])
    return n


def struct_1st_level(s):
    """Returns number of fields in Struct"""
    return len(s.__dict__)
