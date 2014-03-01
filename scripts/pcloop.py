import threading
try:
    import Queue as queue
except ImportError:
    import queue
from collections import deque
from time import sleep, time
from xmlreader import XMLReader
import helpers
from helpers import Struct
from math import sqrt
import sys

import pose
import simobject
import supervisor

import gc

PAUSE = 0
RUN = 1
# RUN_ONCE = 2 # This loop cannot run once
DRAW_ONCE = 3

class PCLoop(threading.Thread):
    """The PCLoop manages the connection between an external robot and a locally running
       supervisor. It also tries to draw a part of the world, using the supplied *renderer*.
       
       This loop only supports one robot per world file and no obstacles.
       
       The simulator runs in a separate thread. None of its functions are thread-safe,
       and should never be called directly from other objects (except for the functions
       inherited from `threading.Thread`). The communication with the simulator
       should be done through its *in_queue* and *out_queue*. See :ref:`ui-sim-queue`.
       
       :param renderer: The renderer that will be used to draw the world.
                        The simulator will assume control of the renderer.
                        The renderer functions also have to be considered thread-unsafe.
       :type renderer: :class:`~renderer.Renderer`
       :param in_queue: The queue that is used to send events to the simulator.
       :type in_queue: :class:`Queue.Queue`
    """
    
    __nice_colors = (0x55AAEE, 0x66BB22, 0xFFBB22, 0xCC66AA,
                     0x77CCAA, 0xFF7711, 0xFF5555, 0x55CC88)

    def __init__(self, renderer, in_queue):
        """Create a simulator with *renderer* and *in_queue*
        """
        super(PCLoop, self).__init__()

        #Attributes
        self.__stop = False
        self.__state = PAUSE
        self.__renderer = renderer
        self.__center_on_robot = False
        self.__orient_on_robot = False
        self.__show_sensors = True
        self.__draw_supervisors = False
        self.__show_tracks = True
        
        self.__in_queue = in_queue
        self._out_queue = queue.Queue()

        # Zoom on scene - Move to read_config later
        self.__time = 0.0

        # World objects
        self.__robot = None
        self.__tracker = None
        self.__supervisor = None
        self.__background = []
        self.__zoom_default = 1

        self.__world = None
        
        self.__log_queue = deque()
        
    def read_config(self, filename):
        '''Load in the objects from the world XML file '''

        self.log('reading initial configuration')
        try:
            self.__world = XMLReader(filename, 'simulation').read()
        except Exception as e:
            raise Exception('[PCLoop.read_config] Failed to parse ' + filename \
                + ': ' + str(e))
        else:
            self.__supervisor_param_cache = None
            self.__center_on_robot = False
            if self.__robot is not None:
                r = self.__robot
                self.__robot = None
                del r
                del self.__supervisor
                self.__supervisor = None
                gc.collect(r)
                print(gc.get_referrers(r))
            self.__construct_world()

    def __construct_world(self):
        """Creates objects previously loaded from the world xml file.
           
           This function uses the world in ``self.__world``.
           
           All the objects will be created anew, including robots and supervisors.
           All of the user's code is reloaded.
        """
        if self.__world is None:
            return

        helpers.unload_user_modules()

        self.__state = DRAW_ONCE            
            
        if self.__robot is not None:
            del self.__robot
            self.__robot = None
            del self.__supervisor
            self.__supervisor = None
            del self.tracker

        self.__background = []
        
        for thing in self.__world:
            if thing.type == 'robot' and self.__robot is None:
                try:
                    robot_class = helpers.load_by_name(thing.robot.type,'robots')
                    if thing.robot.options is not None:
                        self.__robot = robot_class(thing.robot.pose, options = Struct(thing.robot.options))
                    else:
                        self.__robot = robot_class(thing.robot.pose)
                    self.__robot.set_logqueue(self.__log_queue)
                    if thing.robot.color is not None:
                        self.__robot.set_color(thing.robot.color)
                    else:
                        self.__robot.set_color(self.__nice_colors[0])
                        
                    # Create supervisor
                    sup_class = helpers.load_by_name(thing.supervisor.type,'supervisors')
                    
                    info = self.__robot.get_info()
                    info.color = self.__robot.get_color()
                    if thing.supervisor.options is not None:
                        self.__supervisor = sup_class(thing.robot.pose, info, options = Struct(thing.supervisor.options))
                    else:
                        self.__supervisor = sup_class(thing.robot.pose, info)                        
                    self.__supervisor.set_logqueue(self.__log_queue)
                    name = "Robot {}".format(sup_class.__name__)
                    if self.__supervisor_param_cache is not None:
                        self.__supervisor.set_parameters(self.__supervisor_param_cache)
                    self._out_queue.put(("make_param_window",
                                            (self.__robot, name,
                                             self.__supervisor.get_ui_description())))
                   
                    # Create trackers
                    self.__tracker = simobject.Path(thing.robot.pose,self.__robot.get_color())
                except:
                    self.log("[PCLoop.construct_world] Robot creation failed!")
                    if self.__robot is not None:
                        del self.__robot
                        self.__robot = None
                    self.__supervisor = None
                    gc.collect()
                    raise
                    #raise Exception('[PCLoop.construct_world] Unknown robot type!')
            elif thing.type == 'marker':
                if thing.polygon.color is None:
                    thing.polygon.color = 0x00FF00
                self.__background.append(
                    simobject.Polygon(thing.polygon.pose,
                                      thing.polygon.points,
                                      thing.polygon.color))
            else:
                raise Exception('[PCLoop.construct_world] Unknown object: '
                                + str(thing.type))
                                
        self.__time = 0.0
        if self.__robot is None:
            raise Exception('[PCLoop.construct_world] No robot specified!')
        else:
            self.__recalculate_default_zoom()
            if not self.__center_on_robot:
                self.focus_on_world()
            self.__supervisor_param_cache = None
            self.__state = DRAW_ONCE
            
        self._out_queue.put(('reset',()))

    def __recalculate_default_zoom(self):
        """Calculate the zoom level that will show the robot at about 10% its size
        """
        xmin, ymin, xmax, ymax = self.__robot.get_bounds()
        maxsize = sqrt(float(xmax-xmin)**2 + float(ymax-ymin)**2)
        if maxsize == 0:
            self.__zoom_default = 1
        else:
            self.__zoom_default = max(self.__renderer.size)/maxsize/10
            
    def __reset_world(self):
        """Resets the world and objects to starting position.
        
           All the user's code will be reloaded.
        """
        if self.__world is None:
            return
        if self.__supervisor is not None:
            self.__supervisor_param_cache = self.__supervisor.get_parameters()
            del self.__supervisor
            self.__supervisor = None
        if self.__robot is not None:
            del self.__robot
            self.__robot = None
        self.__construct_world()

    def run(self):
        """Start the thread. In the beginning there's no world, no obstacles
           and no robots.
           
           The simulator will try to draw the world undependently of the
           simulation status, so that the commands from the UI get processed.
        """
        self.log('starting simulator thread')

        time_constant = 0.02 # 20 milliseconds
        
        self.__renderer.clear_screen() #create a white screen
        self.__update_view()

        self.__time = time()

        while not self.__stop:
# 
            try:

                self.__process_queue()

                if self.__state == RUN:

#                    self.__time += time_constant
                                      
                    self.__robot.update_external_info()
                    self.fwd_logqueue()
                    
                    new_time = time()
                    
                    # Now calculate supervisor outputs for the new position
                    inputs = self.__supervisor.execute(self.__robot.get_info(), new_time - self.__time)
                    self.__time = new_time
                    self.fwd_logqueue()
                    self.__robot.set_inputs(inputs)
                    self.fwd_logqueue()
                    self.__robot.set_pose(self.__supervisor.pose_est)
                    self.__tracker.add_point(self.__supervisor.pose_est)
                    self.fwd_logqueue()

                else:
                    sleep(time_constant)

                # Draw to buffer-bitmap
                if self.__state != PAUSE:
                    self.__draw()
                    
                if self.__state == DRAW_ONCE:
                    self.pause_simulation()

                self.fwd_logqueue()
  
            except RuntimeError as e:
                self.log(str(e))
            except Exception as e:
                self._out_queue.put(("exception",sys.exc_info()))
                self.pause_simulation()
                self.fwd_logqueue()

    def __draw(self):
        """Draws the world and items in it.
        
           This will draw the markers, the obstacles,
           the robots, their tracks and their sensors
        """
        
        if self.__robot is not None and self.__center_on_robot:
            if self.__orient_on_robot:
                self.__renderer.set_screen_center_pose(self.__robot.get_pose())
            else:
                self.__renderer.set_screen_center_pose(pose.Pose(self.__robot.get_pose().x, self.__robot.get_pose().y, 0.0))

        self.__renderer.clear_screen()
        if self.__draw_supervisors and self.__supervisor is not None:
            self.__supervisor.draw_background(self.__renderer)
        for bg_object in self.__background:
            bg_object.draw(self.__renderer)

        # Draw the robot, tracker and sensors after obstacles
        if self.__show_tracks and self.__tracker is not None:
            self.__tracker.draw(self.__renderer)
        if self.__robot is not None:
            self.__robot.draw(self.__renderer)
            if self.__show_sensors:
                self.__robot.draw_sensors(self.__renderer)

        if self.__draw_supervisors and self.__supervisor is not None:
            self.__supervisor.draw_foreground(self.__renderer)

        # update view
        self.__update_view()

    def __update_view(self):
        """Signal the UI that the drawing process is finished,
           and it is safe to access the renderer.
        """
        self._out_queue.put(('update_view',()))
        self._out_queue.join() # wait until drawn

    def __draw_once(self):
        if self.__state == PAUSE:
            self.__state = DRAW_ONCE
            
    def refresh(self):
        self.__draw_once()
        
    def focus_on_world(self):
        """Scale the view to include all of the world (including robots)"""
        def include_bounds(bounds, o_bounds):
            xl, yb, xr, yt = bounds
            xlo, ybo, xro, yto = o_bounds
            if xlo < xl: xl = xlo
            if xro > xr: xr = xro
            if ybo < yb: yb = ybo
            if yto > yt: yt = yto
            return xl, yb, xr, yt
        
        def bloat_bounds(bounds, factor):
            xl, yb, xr, yt = bounds
            w = xr-xl
            h = yt-yb
            factor = (factor-1)/2.0
            return xl - w*factor, yb - h*factor, xr + w*factor, yt + h*factor
            
        self.__center_on_robot = False
        bounds = self.__robot.get_bounds()
        for bgobject in self.__background:
            bounds = include_bounds(bounds, bgobject.get_bounds())
        xl, yb, xr, yt = bounds
        self.__renderer.set_view_rect(xl,yb,xr-xl,yt-yb)
        self.__draw_once()

    def focus_on_robot(self, rotate = True):
        """Center the view on the robot and follow it.
        
           If *rotate* is true, also follow the robot's orientation.
        """
        self.__center_on_robot = True
        self.__orient_on_robot = rotate
        self.__draw_once()

    def show_sensors(self, show = True):
        """Show or hide the robots' sensors on the simulation view
        """
        self.__show_sensors = show
        self.__draw_once()

    def show_tracks(self, show = True):
        """Show/hide tracks for every robot on simulator view"""
        self.__show_tracks = show
        self.__draw_once()

    def show_supervisors(self, show = True):
        """Show/hide the information from the supervisors"""
        self.__draw_supervisors = show
        self.__draw_once()

    def show_grid(self, show=True):
        """Show/hide gridlines on simulator view"""
        self.__renderer.show_grid(show)
        self.__draw_once()

    def adjust_zoom(self,factor):
        """Zoom the view by *factor*"""
        self.__renderer.set_zoom_level(self.__zoom_default*factor)
        self.__draw_once()
        
    def apply_parameters(self,robot,parameters):
        """Apply *parameters* to the supervisor of *robot*.
        
        The parameters have to correspond to the requirements of the supervisor,
        as specified in :meth:`supervisor.Supervisor.get_ui_description`
        """
        if self.__robot == robot:
            self.__supervisor.set_parameters(parameters)
            self.__draw_once()
        else:
            self.log("Robot not found")

    # Stops the thread
    def stop(self):
        """Stop the simulator thread when the entire program is closed"""
        self.log('stopping simulator thread')
        self.__stop = True
        self._out_queue.put(('stopped',()))

    def start_simulation(self):
        """Start/continue the simulation"""
        if self.__robot is not None:
            self.__robot.resume()
            self.__state = RUN
            self._out_queue.put(('running',()))

    def pause_simulation(self):
        """Pause the simulation"""
        if self.__robot is not None:
            self.__robot.pause()
        self.__state = PAUSE
        self._out_queue.put(('paused',()))

    def reset_simulation(self):
        """Reset the simulation to the start position"""
        if self.__robot is not None:
            self.__robot.reset()
        self.__state = DRAW_ONCE
        self.__reset_world()

### FIXME Those two functions are not thread-safe
    def get_time(self):
        """Get the internal simulator time."""
        return time() - self.__time

    def is_running(self):
        """Get the simulation state as a `bool`"""
        return self.__state == RUN
###------------------

    def __process_queue(self):
        """Process external calls
        """
        while not self.__in_queue.empty():
            tpl = self.__in_queue.get()
            if isinstance(tpl,tuple) and len(tpl) == 2:
                name, args = tpl
                if name in self.__class__.__dict__:
                    try:
                        self.__class__.__dict__[name](self,*args)
                    except TypeError:
                        self.log("Wrong simulator event parameters {}{}".format(name,args))
                        self._out_queue.put(("exception",sys.exc_info()))
                    except Exception as e:
                        self._out_queue.put(("exception",sys.exc_info()))
                else:
                    self.log("Unknown simulator event '{}'".format(name))
            else:
                self.log("Wrong simulator event format '{}'".format(tpl))
            self.__in_queue.task_done()
    
    def log(self, message, obj=None):
        if obj is None:
            obj = self
        print("{}: {}".format(obj.__class__.__name__,message))
        self._out_queue.put(("log",(message,obj.__class__.__name__,None)))
        
    def fwd_logqueue(self):
        while self.__log_queue:
            obj, message = self.__log_queue.popleft()
            
            color = None
            # Get the color
            if isinstance(obj,simobject.SimObject):
                color = obj.get_color()
            elif isinstance(obj,supervisor.Supervisor):
                color = obj.robot_color
                
            self._out_queue.put(("log",(message,obj.__class__.__name__,color)))
    
#end class Simulator

