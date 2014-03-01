try:
    import Queue as queue
except ImportError:
    import queue

from helpers import Struct

class uiParameter(Struct):
    """uiParameter represents a single GUI element that is used to build a parameter window
       in the UI (simulator event "make_param_window").
       
       It has one parameter, ``type``, that defines the type of the parameter. Possible parameter
       types are GROUP, INT, FLOAT, BOOL and SELECT.
    """
    
    GROUP, INT, FLOAT, BOOL, SELECT = 0,1,2,3,4
    
    def __init__(self, elem_type):
        self.type = elem_type

class uiGroup(uiParameter):
    def __init__(self, contents):
        uiParameter.__init__(uiParameter.GROUP)
        self.contents = contents

class uiInt(uiParameter):
    def __init__(self, value, min_value = -100, max_value = 100):
        uiParameter.__init__(self, uiParameter.INT)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value

class uiFloat(uiParameter):
    def __init__(self, value, step = 1.0, min_value = -1000.0, max_value = 1000.0):
        uiParameter.__init__(self, uiParameter.FLOAT)
        self.value = value
        self.step = step
        self.min_value = min_value
        self.max_value = max_value

class uiBool(uiParameter):
    def __init__(self, value):
        uiParameter.__init__(self, uiParameter.BOOL)
        self.value = value

class uiSelect(uiParameter):
    def __init__(self, value, value_list):
        uiParameter.__init__(self, uiParameter.SELECT, value, value_list)
        self.value = value
        self.value_list = value_list
    
class SimUI:
    """The SimUI class defines a front-end for the :class:`~simulator.Simulator`.
       It contains the necessary functions for the frontend-simulator communication
       and stubs for the message callbacks.
       
       This class manages three important objects:
       
       * The simulator, as ``self.simulator_thread``
       * The incoming simulator events, as ``self.in_queue``
       * The outgoing simulator commands, as ``self.sim_queue``
       
       The constructor of SimUI takes a :class:`~renderer.Renderer` object as parameter.
       This renderer will be passed to the simulator to draw on.
    """
    def __init__(self, renderer, simulator_class):
         
        self.event_handler = None
        
        self.sim_queue = queue.Queue()
         
         # create the simulator thread
        self.simulator_thread = simulator_class(renderer, self.sim_queue)

        self.in_queue = self.simulator_thread._out_queue
        
        self.simulator_thread.start()
    
    def register_event_handler(self, event_handler):
        """Register a callback that will be executed to process the 
        """
        self.event_handler = event_handler
        
    def unregister_event_handler(self):
        """Unregister a previously registered event handler.
        """
        self.event_handler = None
        
    def process_events(self, process_all = False):
        """Processes one or all incoming events from the simulator. A single
           event is a tuple (name,args). During the processing of the event,
           the function ``simulator_``\ *name* will be called with args as parameters.
           
           It is strongly discouraged to create new class methods with the name
           starting with `simulator_`. Such functions could be called from
           the simulator without your consent.
           
           Unknown or malformed events will lead to an error message printed
           to the console.
        """
        while not self.in_queue.empty():
            tpl = self.in_queue.get()
            if isinstance(tpl,tuple) and len(tpl) == 2:
                name, args = tpl
                
                intercepted = False
                if self.event_handler is not None:
                    intercepted = self.event_handler(name,args)
                    
                if not intercepted:
                    # Scramble
                    name = "simulator_{}".format(name)
                    if name in self.__class__.__dict__:
                        try:
                            self.__class__.__dict__[name](self,*args)
                        except TypeError:
                            print("Wrong UI event parameters {}{}".format(name,args))
                            raise
                    else:
                        print("Unknown UI event '{}'".format(name))
            else:
                print("Wrong UI event format '{}'".format(tpl))
            self.in_queue.task_done()
            if not process_all:
                return
    
    def run_simulator_command(self,command,*args):
        """Sends the command *command* to the simulator. All arguments after
           *command* are passed to the command processing function on the simulator side.
           
           See :class:`~simulator.Simulator` for the available commands.
        """
        self.sim_queue.put((command, args))

    # Simulator processing functions : stubs

    def simulator_make_param_window(self,robot_id,name,parameters):
        """A request from the supervisor to create a parameter window.
           *robot_id* is guaranteed to uniquely identify a robot in a simulation.
           Currently, *robot_id* is the actual robot object.
           It can be used e.g. to extract the color of the robot as ``robot_id.get_color()``.
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
        
    def simulator_exception(self,e_type, e_value, e_traceback):
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
    
    #def get_view_parameters(self):
        #pass
    
    #def set_view_parameters(self,params):
        #pass
    
    #def new_renderer(self):
        #pass
    
    #def pop_renderer(self):
        #pass

    #def start_test(self):
        #"""This function will pause and 'cache' the currently running
           #simulation. A new `simulator.Simulator` will be started with
           #the control belonging to the tester object.
        #"""
        #self.antiteststruct = Struct()
        #self.antiteststruct.wasrunning = False
        ## 1) Pause simulator
        #if self.simulator_thread.is_running():
            #self.antiteststruct.wasrunning = True # Remember the setting
            #self.run_simulator_command('pause_simulation') # Pause simulation
            #self.process_events(True) # Process all events
            
        ## 2) Create new simulator
        #self.antiteststruct.simulator = simulator_thread
        #self.simulator_thread = sim.Simulator(self.instantiate_new_renderer(), self.sim_queue)
        #self.simulator_thread.start()
    
    #def stop_test(self):
        #"""This function will restore the cached simulation and 
           #simulation. A new `simulator.Simulator` will be started with
           #the control belonging to the tester object.
        #"""
        #view_params = self.get_view_parameters()
        
        ## 1) Stop simulator
        #self.run_simulator_command('stop')
        #while self.simulator_thread.isAlive():
            #self.process_events(True)
            #self.simulator_thread.join(0.1)
                
        ## 2) Switch to old simulator
        #self.pop_renderer()
        #self.simulator_thread = self.antiteststruct.simulator
        
        ## 3) continue running
        #if self.antiteststruct.wasrunning:
            #self.run_simulator_command('pause_simulation')
