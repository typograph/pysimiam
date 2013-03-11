import threading
import Queue as queue
from time import sleep, clock
from xmlreader import XMLReader
import helpers
from math import sqrt
import sys

import pose
import simobject
from quadtree import QuadTree, Rect

PAUSE = 0
RUN = 1

class Simulator(threading.Thread):
    """The simulator manages simobjects and their collisions, commands supervisors
       and draws the world using the supplied *renderer*.
       
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
        super(Simulator, self).__init__()

        #Attributes
        self.__stop = False
        self.__state = PAUSE
        self.__renderer = renderer
        self.__center_on_robot = False
        self.__orient_on_robot = False
        self.__show_sensors = True
        self.__show_tracks = True
        
        self.__in_queue = in_queue
        self._out_queue = queue.Queue()

        # Zoom on scene - Move to read_config later
        self.__time_multiplier = 1.0
        self.__time = 0.0

        # World objects
        self.__robots = []
        self.__trackers = []
        self.__obstacles = []
        self.__supervisors = []
        self.__background = []
        self.__zoom_default = 1

        self.__world = None
        
        # Internal objects
        self.__qtree = None

    def read_config(self, filename):
        '''Load in the objects from the world XML file '''

        print 'reading initial configuration'
        try:
            self.__world = XMLReader(filename, 'simulation').read()
        except Exception, e:
            raise Exception('[Simulator.read_config] Failed to parse ' + filename \
                + ': ' + str(e))
        else:
            self.__supervisor_param_cache = None
            self.__center_on_robot = False
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

        self.__state = PAUSE            
            
        self.__robots = []
        self.__obstacles = []
        self.__supervisors = []
        self.__background = []
        self.__trackers = []
        self.__qtree = None
        
        for thing in self.__world:
            thing_type = thing[0]
            if thing_type == 'robot':
                robot_type, supervisor_type, robot_pose, robot_color  = thing[1:5]
                try:
                    # Create robot
                    robot_class = helpers.load_by_name(robot_type,'robots')
                    robot = robot_class(pose.Pose(robot_pose))
                    if robot_color is not None:
                        robot.set_color(robot_color)
                    elif len(self.__robots) < 8:
                        robot.set_color(self.__nice_colors[len(self.__robots)])
                        
                    # Create supervisor
                    sup_class = helpers.load_by_name(supervisor_type,'supervisors')
                    
                    info = robot.get_info()
                    info.color = robot.get_color()
                    supervisor = sup_class(robot.get_pose(), info)                    
                    name = "Robot {}: {}".format(len(self.__robots)+1, sup_class.__name__)
                    if self.__supervisor_param_cache is not None:
                        supervisor.set_parameters(self.__supervisor_param_cache[len(self.__supervisors)])
                    self._out_queue.put(("make_param_window",
                                            (robot, name,
                                             supervisor.get_ui_description())))
                    self.__supervisors.append(supervisor)
                    
                    # append robot after supervisor for the case of exceptions
                    self.__robots.append(robot)
                    
                    # Create trackers
                    self.__trackers.append(simobject.Path(robot.get_pose(),robot))
                    self.__trackers[-1].set_color(robot.get_color())
                except:
                    print "[Simulator.construct_world] Robot creation failed!"
                    raise
                    #raise Exception('[Simulator.construct_world] Unknown robot type!')
            elif thing_type == 'obstacle':
                obstacle_pose, obstacle_coords, obstacle_color = thing[1:4]
                if obstacle_color is None:
                    obstacle_color = 0xFF0000
                self.__obstacles.append(
                    simobject.Polygon(pose.Pose(obstacle_pose),
                                      obstacle_coords,
                                      obstacle_color))
            elif thing_type == 'marker':
                obj_pose, obj_coords, obj_color = thing[1:4]
                if obj_color is None:
                    obj_color = 0x00FF00
                self.__background.append(
                    simobject.Polygon(pose.Pose(obj_pose),
                                      obj_coords,
                                      obj_color))
            else:
                raise Exception('[Simulator.construct_world] Unknown object: '
                                + str(thing_type))
                                
        self.__time = 0.0
        if not self.__robots:
            raise Exception('[Simulator.construct_world] No robot specified!')
        else:
            self.__recalculate_default_zoom()
            if not self.__center_on_robot:
                self.focus_on_world()
            self.__draw()
            self.__supervisor_param_cache = None
            
        self.__state = PAUSE            

        self._out_queue.put(('reset',()))

    def __recalculate_default_zoom(self):
        """Calculate the zoom level that will show the robot at about 10% its size
        """
        maxsize = 0
        for robot in self.__robots:
            xmin, ymin, xmax, ymax = robot.get_bounds()
            maxsize = max(maxsize,sqrt(float(xmax-xmin)**2 + float(ymax-ymin)**2))
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
        self.__supervisor_param_cache = [sv.get_parameters() for sv in self.__supervisors ]
        self.__construct_world()

    def run(self):
        """Start the thread. In the beginning there's no world, no obstacles
           and no robots.
           
           The simulator will try to draw the world undependently of the
           simulation status, so that the commands from the UI get processed.
        """
        print 'starting simulator thread'

        time_constant = 0.02 # 20 milliseconds
        
        self.__renderer.clear_screen() #create a white screen
        self.__update_view()

        while not self.__stop:

            try:

                sleep(time_constant/self.__time_multiplier)

                if self.__state == RUN:

                    for i, supervisor in enumerate(self.__supervisors):
                        info = self.__robots[i].get_info()
                        inputs = supervisor.execute( info, time_constant)
                        self.__robots[i].set_inputs(inputs)

                    self.__time += time_constant

                    for i, robot in enumerate(self.__robots):
                        robot.move(time_constant)
                        self.__trackers[i].add_point(robot.get_pose())

                    # the parameters that might have been changed have no effect
                    # on collisions
                    if self.__check_collisions():
                        print "Collision detected!"
                        self.__state = PAUSE
                        #self.__stop = True

                # Draw to buffer-bitmap
                self.__draw()
            
            except Exception as e:
                self._out_queue.put(("exception",sys.exc_info()))
                self.pause_simulation()

    def __draw(self):
        """Draws the world and items in it.
        
           This will draw the markers, the obstacles,
           the robots, their tracks and their sensors
        """
        self.__process_queue()

        if self.__robots and self.__center_on_robot:
            # Temporary fix - center onto first robot
            robot = self.__robots[0]
            if self.__orient_on_robot:
                self.__renderer.set_screen_center_pose(robot.get_pose())
            else:
                self.__renderer.set_screen_center_pose(pose.Pose(robot.get_pose().x, robot.get_pose().y, 0.0))

        self.__renderer.clear_screen()

        for supervisor in self.__supervisors:
            supervisor.draw(self.__renderer)

        for bg_object in self.__background:
            bg_object.draw(self.__renderer)
        for obstacle in self.__obstacles:
            obstacle.draw(self.__renderer)

        # Draw the robots, trackers and sensors after obstacles
        if self.__show_tracks:
            for tracker in self.__trackers:
                tracker.draw(self.__renderer)
        for robot in self.__robots:
            robot.draw(self.__renderer)
            if self.__show_sensors:
                robot.draw_sensors(self.__renderer)

        # update view
        self.__update_view()

    def __update_view(self):
        """Signal the UI that the drawing process is finished,
           and it is safe to access the renderer.
        """
        self._out_queue.put(('update_view',()))
        self._out_queue.join() # wait until drawn
        
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
        bounds = self.__robots[0].get_bounds()
        for robot in self.__robots:
            bounds = include_bounds(bounds, bloat_bounds(robot.get_bounds(),4))
        for obstacle in self.__obstacles:
            bounds = include_bounds(bounds, obstacle.get_bounds())
        xl, yb, xr, yt = bounds
        self.__renderer.set_view_rect(xl,yb,xr-xl,yt-yb)

    def focus_on_robot(self, rotate = True):
        """Center the view on the (first) robot and follow it.
        
           If *rotate* is true, also follow the robot's orientation.
        """
        self.__center_on_robot = True
        self.__orient_on_robot = rotate

    def show_sensors(self, show = True):
        """Show or hide the robots' sensors on the simulation view
        """
        self.__show_sensors = show

    def show_tracks(self, show = True):
        """Show/hide tracks for every robot on simulator view"""
        self.__show_tracks = show

    def show_grid(self, show=True):
        """Show/hide gridlines on simulator view"""
        self.__renderer.show_grid(show)

    def adjust_zoom(self,factor):
        """Zoom the view by *factor*"""
        self.__renderer.set_zoom_level(self.__zoom_default*factor)
        
    def apply_parameters(self,robot,parameters):
        """Apply *parameters* to the supervisor of *robot*.
        
        The parameters have to correspond to the requirements of the supervisor,
        as specified in :meth:`supervisor.Supervisor.get_ui_description`
        """
        index = self.__robots.index(robot)
        if index < 0:
            print "Robot not found"
        else:
            self.__supervisors[index].set_parameters(parameters)

    # Stops the thread
    def stop(self):
        """Stop the simulator thread when the entire program is closed"""
        print 'stopping simulator thread'
        self.__stop = True
        self._out_queue.put(('stopped',()))

    def start_simulation(self):
        """Start/continue the simulation"""
        if self.__robots:
            self.__state = RUN
            self._out_queue.put(('running',()))

    def pause_simulation(self):
        """Pause the simulation"""
        self.__state = PAUSE
        self._out_queue.put(('paused',()))

    def reset_simulation(self):
        """Reset the simulation to the start position"""
        self.__state = PAUSE
        self.__reset_world()

    def set_time_multiplier(self,multiplier):
        """Shorten the interval between evaluation cycles by *multiplier*,
           speeding up the simulation"""
        self.__time_multiplier = multiplier

### FIXME Those two functions are not thread-safe
    def get_time(self):
        """Get the internal simulator time."""
        return self.__time

    def is_running(self):
        """Get the simulation state as a `bool`"""
        return self.__state == RUN
###------------------

    def __check_collisions(self):
        """Update proximity sensors and detect collisions between objects"""
        
        collisions = []
        checked_robots = []
        
        if self.__qtree is None:
            self.__qtree = QuadTree(self.__obstacles)
            
        if len(self.__robots) > 1:
            rqtree = QuadTree(self.__robots)
        else: rqtree = None
        
        # check each robot
        for robot in self.__robots:
                
            # update proximity sensors
            for sensor in robot.get_external_sensors():
                sensor.get_world_envelope(True)
                rect = Rect(sensor.get_bounding_rect())
                sensor.update_distance()
                # distance to obstacles
                for obstacle in self.__qtree.find_items(rect):
                    sensor.update_distance(obstacle)
                # distance to other robots
                if rqtree is None: continue
                for other in rqtree.find_items(rect):
                    if other is not robot:
                        sensor.update_distance(other)
            
            rect = Rect(robot.get_bounding_rect())
            
            # against nearest obstacles
            for obstacle in self.__qtree.find_items(rect):
                if robot.has_collision(obstacle):
                    collisions.append((robot, obstacle))
            
            # against other robots
            if rqtree is not None:
                for other in rqtree.find_items(rect):
                    if other is robot: continue
                    if other in checked_robots: continue
                    if robot.has_collision(other):
                        collisions.append((robot, other))

            checked_robots.append(robot)
            
        if len(collisions) > 0:
            # Test code - print out collisions
            for (robot, obstacle) in collisions:
                print "Collision between:\n", robot, "\n", obstacle
            # end of test code
            return True
                
        return False

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
                        print "Wrong simulator event parameters {}{}".format(name,args)
                        self._out_queue.put(("exception",sys.exc_info()))
                    except Exception as e:
                        self._out_queue.put(("exception",sys.exc_info()))
                else:
                    print "Unknown simulator event '{}'".format(name)
            else:
                print "Wrong simulator event format '{}'".format(tpl)
            self.__in_queue.task_done()
    
#end class Simulator
