#
# (c) PySimiam Team
#
# This class was implemented as a weekly programming excercise
# of the 'Control of Mobile Robots' course by Magnus Egerstedt.
#

try:
    import Queue as queue
except ImportError:
    import queue

from .struct import Struct, struct_from_XML, update_struct, struct_volume


class ParameterXMLFormatError(Exception):
    pass


class Parameter:
    """ui.Parameter represents a single GUI element that is used to build
       a parameter window in the UI (simulator event "make_param_window").

       The name of the parameter defines the name of :class:`~helpers.Struct`
       field and the name of XML tag. The name must be a valid python
       ASCII identifier. It is automatically converted to lowercase.

       The label is the text that will be shown in the parameter interface.
       If *label* is not given, the capitalized *name* will be used instead.
    """

    def __init__(self, name, label=None):
        self.name = name.lower()
        if not Struct.is_valid_field_name(name):
            raise ValueError("Invalid Struct field name {}".format(name))
        if label is None:
            self.label = self.name.capitalize()
        else:
            self.label = label

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.name == other.name and
                self.label == other.label and
                self.value == other.value)

    def _load_struct(self, s, lazy):
        if not isinstance(s, type(self.value)):
            if not lazy:
                raise TypeError("The value of {} is of type {}.\
                                {} is not a valid {1}".
                                format(self.name, type(self.value), repr(s)))
        else:
            self.value = s

    def _as_struct(self):
        return self.value

    def _as_xml(self):
        return '{}="{}"'.format(self.name, self.value)


class Int(Parameter):
    """ui.Int represents a single GUI element that is used to input an integer
       value. To limit the range of the value, constructor parameters
       `min_value` and `max_value` can be used. Both limits are inclusive.
    """
    def __init__(self, name, value, min_value=-100, max_value=100, label=None):
        Parameter.__init__(self, name, label)
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError('{} is not a valid integer value'.format(value))
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

    def __eq__(self, other):
        return (Parameter.__eq__(self, other) and
                self.min_value == other.min_value and
                self.max_value == other.max_value)

    def __repr__(self):
        return 'ui.Int("{}", {}, {}, {}, "{}")'.format(self.name,
                                                       self.value,
                                                       self.min_value,
                                                       self.max_value,
                                                       self.label)


class Float(Parameter):
    """ui.Float represents a single GUI element that is used to input
       a floating-point value. To limit the range of the value,
       constructor parameters `min_value` and `max_value` can be used.
       Both limits are inclusive. An additional parameter `step` controls
       the increment value.
    """
    def __init__(self, name, value, step=1.0,
                 min_value=-1000.0, max_value=1000.0, label=None):
        Parameter.__init__(self, name, label)
        if (not isinstance(value, float)
            and (not isinstance(value, int)
                 or isinstance(value, bool))):
            raise ValueError('{} is not a valid float value'.format(value))
        self.value = float(value)
        self.step = float(step)
        self.min_value = float(min_value)
        self.max_value = float(max_value)

    def __eq__(self, other):
        return (Parameter.__eq__(self, other) and
                self.min_value == other.min_value and
                self.max_value == other.max_value and
                self.step == other.step)

    def __repr__(self):
        return 'ui.Float("{}", {}, {}, {}, {}, "{}")'.format(
               self.name, self.value, self.step,
               self.min_value, self.max_value, self.label)


class Bool(Parameter):
    """ui.Bool represents a single GUI element that is used to input
       a true/false value (like a checkbox).
    """
    def __init__(self, name, value, label=None):
        Parameter.__init__(self, name, label)
        if not isinstance(value, bool):
            raise ValueError('{} is not a valid boolean value'.format(value))
        self.value = value

    def _as_xml(self):
        return '{}="{}"'.format(self.name, str(self.value).lower())

    def __repr__(self):
        return 'ui.Bool("{}", {}, "{}")'.format(
               self.name, self.value, self.label)


class Select(Parameter):
    """ui.Select represents a single GUI element that is used to select
       one value from a list of options (like a combobox).
       The possible values need to be supplied in the `value_list` constructor
       parameter.
    """
    def __init__(self, name, value, value_list, label=None):
        if value not in value_list:
            raise ValueError("Singular value in ui.Select: {}".format(value))
        if not isinstance(value, str):
            raise ValueError('{} is not a valid string value'.format(value))
        for val in value_list:
            if not isinstance(val, str):
                raise ValueError('{} is not a valid string value'.format(val))
        Parameter.__init__(self, name, label)
        self.value = value
        self.value_list = value_list

    def __eq__(self, other):
        return (Parameter.__eq__(self, other) and
                self.value_list == other.value_list)

    def _load_struct(self, s, lazy):
        if s not in self.value_list:
            if not lazy:
                raise ValueError("The value of {} is not allowed in {}".
                                 format(s, self.name))
        else:
            self.value = s

    def __repr__(self):
        return 'ui.Select("{}", {}, {}, "{}")'.format(
               self.name, repr(self.value), repr(self.value_list), self.label)


class Group(Parameter):
    """uiGroup represents a parameter group in UI.

       *contents* should be a list of ui elements, contained in this group.
       Each element should be either an instance of :class:`ui.Parameter`,
       or a tuple ``(name, [label, ] value)``, that will be automatically
       converted to :class:`ui.Parameter`. In the latter case the type of the
       GUI element is determined by the type of the value. Specifically,
       a '(value, [value1, value2, ...])' tuple defines a ui.Select, and
       a list of elements in the same form defines a ui.Group.
    """
    def __init__(self, name, contents, label=None):
        Parameter.__init__(self, name, label)
        self.contents = []
        self.__contentsdict = {}
        for e in contents:
            # Accept uiParameter
            if isinstance(e, Parameter):
                if e.name in self.__contentsdict:
                    raise ValueError(
                        "Two parameters with name {} in {}".
                        format(e.name, self.name))
                self.contents.append(e)
                self.__contentsdict[e.name] = e
            # Accept (name, value) and (name, label, value)
            elif isinstance(e, tuple) or isinstance(e, list):
                if len(e) < 2 or len(e) > 3:
                    raise ValueError("Unsupported ui element {}".format(e))
                name = e[0]
                value = e[-1]
                if name in self.__contentsdict:
                    raise ValueError(
                        "Two parameters with name {} in {}".
                        format(name, self.name))
                if len(e) == 3:
                    label = e[1]
                else:
                    label = None
                if isinstance(value, float):
                    self.contents.append(
                        Float(name, value,
                              step=1.0, min_value=-1000.0, max_value=1000.0,
                              label=label))
                elif isinstance(value, bool):
                    self.contents.append(
                        Bool(name, value, label=label))
                elif isinstance(value, int):
                    self.contents.append(
                        Int(name, value,
                            min_value=-100, max_value=100,
                            label=label))
                elif isinstance(value, tuple):
                    self.contents.append(
                        Select(name, value[0], value[1], label=label))
                elif isinstance(value, list):
                    self.contents.append(Group(name, value, label=label))
                else:
                    raise ValueError("Unsupported ui element {}".format(e))
                self.__contentsdict[name] = self.contents[-1]
            else:
                raise ValueError("Unsupported ui element {}".format(e))

    def __eq__(self, other):
        return (isinstance(other, Group) and
                self.name == other.name and
                self.label == other.label and
                self.contents == other.contents)

    def _load_struct(self, s, lazy):
        for elem in self.contents:
            if elem.name in s:
                elem._load_struct(s[elem.name], lazy)
            elif not lazy:
                raise ValueError("Element {} missing in Struct".
                                 format(elem.name))

    def _as_struct(self):
        r = Struct()
        for elem in self.contents:
            r[elem.name] = elem._as_struct()
        return r

    def _as_xml(self):
        attrs = []
        subtags = []
        for elem in self.contents:
            if isinstance(elem, Group):
                subtags += elem._as_xml()  # It's a list
            else:
                attrs.append(elem._as_xml())
        if attrs:
            tag = "{} {}".format(self.name, ' '.join(attrs))
        else:
            tag = self.name

        if subtags:
            return ['<{}>'.format(tag)] + \
                   ["    {}".format(s) for s in subtags] + \
                   ['</{}>'.format(self.name)]
        else:
            return ['<{}/>'.format(tag)]

    def __repr__(self):
        return 'ui.Group("{}", {}, "{}")'.format(self.name,
                                                 repr(self.contents),
                                                 self.label)


class ParamDescr(Group):
    """ParamDescr is the root of ui.Parameter hierarchy. In addition to
       being a ui.Group it also defines several utility methods for converting
       to :class:`~helpers.Struct`, JSON and XML.
    """
    def __init__(self, *elements):
        Group.__init__(self, "parameters", elements)

    def loadFromXML(self, handle, lazy=True):
        """Load parameter values from an XML file.
           The `handle` parameter should either be a file object
           or a filename string.

           Malformed XML or an XML structure not conforming to the schema
           defined by saveToXML will raise an exception.
        """
        if isinstance(handle, str):
            with open(handle, "r") as f:
                self.loadFromXML(f)
        else:
            backup = self._as_struct()
            l_backup = len(backup)
            try:
                news = struct_from_XML(handle.read(),
                                       lazy=lazy,
                                       root="parameters")
                l_news = len(news)
                if not lazy and struct_volume(news) != struct_volume(backup):
                    raise ParameterXMLFormatError(
                        "XML doesn't completely describe Struct")
                u, i = update_struct(backup, news, lazy)

                if not lazy and (i > 0 or u < l_backup):
                    raise ValueError(
                        "Failed to fully use XML: {}/{} updated, {}/{} used".
                        format(u, l_backup, l_news-i, l_news))
                else:
                    self.loadStruct(backup, lazy)
            except ValueError as e:
                raise ParameterXMLFormatError(str(e))

    def saveToXML(self, handle):
        """Save parameter values to an XML file.
           The `handle` parameter should either be a file object
           or a filename string.

           The schema of the resulting XML is defined by the specific
           ui.Parameter hierarchy. Every :class:`ui.Group` is converted
           to an XML tag, every other :class:`ui.Parameter` to an attribute
           of the tag belonging to the parent :class:`ui.Group`. The names
           of the tags and attributes are the names of the
           :class:`ui.Parameter` elements. The outer :class:`ui.Group` is
           named `parameter`.
        """
        if isinstance(handle, str):
            with open(handle, "w") as f:
                self.loadFromXML(f)
        else:
            handle.write('<?xml version="1.0"?>\n')
            for tag in self._as_xml():
                handle.write(tag)
                handle.write('\n')

    def loadStruct(self, struct, lazy=True):
        """Load the values of parameters from a :class:`~helpers.Struct`.
           The loader is lazy by default, and will ignore extra fields
           and missing fields in `struct`. Setting `lazy` to False will
           lead to exceptions being raised on non-conforming `struct`.
        """
        self._load_struct(struct, lazy)

    def asStruct(self):
        return self._as_struct()


class SimUI(object):
    """The SimUI class defines a front-end for
       the :class:`~simulator.Simulator`.
       It contains the necessary functions for the frontend-simulator
       communication and stubs for the message callbacks.

       This class manages three important objects:

       * The simulator, as ``self.simulator_thread``
       * The incoming simulator events, as ``self.in_queue``
       * The outgoing simulator commands, as ``self.sim_queue``

       The constructor of SimUI takes a :class:`~renderer.Renderer`
       object as parameter. This renderer will be passed to the simulator
       to draw on.
    """
    def __init__(self, renderer, simulator_class):

        self.event_handler = None

        self.sim_queue = queue.Queue()

        # create the simulator thread
        self.simulator_thread = simulator_class(renderer, self.sim_queue)

        self.in_queue = self.simulator_thread._out_queue

        self.simulator_thread.start()

    def register_event_handler(self, event_handler):
        """Register a callback that will be executed to process
           the incoming events before they are processed by SimUI.

           The callback function needs to return a boolean value indicating
           whether the event was intercepted by the event handler.
           If the value is True, the event is discarded, otherwise
           it is processed in the usual manner.
        """
        self.event_handler = event_handler

    def unregister_event_handler(self):
        """Unregister a previously registered event handler."""
        self.event_handler = None

    def process_events(self, process_all=False):
        """Processes one or all incoming events from the simulator. A single
           event is a tuple (name, args). During the processing of the event,
           the function ``simulator_``\ *name* will be called with `args`
           as parameters.

           It is strongly discouraged to create new class methods with the name
           starting with `simulator_`. Such functions could be called from
           the simulator without your consent.

           Unknown or malformed events will lead to an error message printed
           to the console.
        """
        while not self.in_queue.empty():
            tpl = self.in_queue.get()
            if isinstance(tpl, tuple) and len(tpl) == 2:
                name, args = tpl

                intercepted = False
                if self.event_handler is not None:
                    intercepted = self.event_handler(name, args)

                if not intercepted:
                    # Scramble
                    name = "simulator_{}".format(name)
                    if name in self.__class__.__dict__:
                        try:
                            self.__class__.__dict__[name](self, *args)
                        except TypeError:
                            print("Wrong UI event parameters {}{}".
                                  format(name, args))
                            raise
                    else:
                        print("Unknown UI event '{}'".format(name))
            else:
                print("Wrong UI event format '{}'".format(tpl))
            self.in_queue.task_done()
            if not process_all:
                return

    def run_simulator_command(self, command, *args):
        """Sends the command *command* to the simulator. All arguments after
           *command* are passed to the command processing function
           on the simulator side.

           See :class:`~simulator.Simulator` for the available commands.
        """
        self.sim_queue.put((command, args))

    # Simulator processing functions : stubs

    def simulator_make_param_window(self, robot_id, name, parameters):
        """A request from the supervisor to create a parameter window.
           *robot_id* is guaranteed to uniquely identify a robot
           in a simulation.
           Currently, *robot_id* is the actual robot object.
           It can be used e.g. to extract the color of the robot
           as ``robot_id.color``.
           *name* is the desired window name, and *parameters* is the structure
           returned by :meth:`~supervisor.Supervisor.get_ui_description`.
        """
        raise NotImplementedError('SimUI.simulator_make_param_window')

    def simulator_running(self):
        """A notification that the simulation has been started."""
        raise NotImplementedError('SimUI.simulator_running')

    def simulator_paused(self):
        """A notification that the simulation has been paused."""
        raise NotImplementedError('SimUI.simulator_paused')

    def simulator_reset(self):
        """A notification that the simulation has been reset."""
        raise NotImplementedError('SimUI.simulator_reset')

    def simulator_stopped(self):
        """A notification that the simulation has been stopped."""
        raise NotImplementedError('SimUI.simulator_stopped')

    def simulator_update_view(self):
        """A request to redraw the simulation window. This notification
           signifies that the simulation has stopped using the renderer,
           and is waiting for the UI to process this event.

           The simulation will be resumed after this function exits.
        """
        raise NotImplementedError('SimUI.simulator_update_view')

    def simulator_exception(self, e_type, e_value, e_traceback):
        """An exception was raised in the simulator thread in the attempt
           to process an incoming command.
        """
        raise NotImplementedError('SimUI.simulator_exception')

    def simulator_log(self, message, objclass, objcolor):
        """A log *message* was generated by one of the simulation objects
           of class *objclass*. The *objcolor* is the color of the simobject,
           in the case the object is connected to one, and None otherwise.
        """
        raise NotImplementedError('SimUI.simulator_log')

    # Commands for the tester:

    def run_simulation(self):
        """Unpause the simulation."""
        self.run_simulator_command('start_simulation')

    def pause_simulation(self):
        """Pause the simulation."""
        self.run_simulator_command('pause_simulation')

    def step_simulation(self):
        """Advance the simulation one step if it is paused."""
        self.run_simulator_command('step_simulation')

    def start_testing(self):
        """Prepare the simulation environment for testing, e.g. disable
           user controls of the simulation progress."""
        pass

    def stop_testing(self):
        """Return UI back to normal operation."""
        pass
