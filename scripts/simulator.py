"""Simulator Thread
"""
import threading
import Queue as queue
from time import sleep, clock
from xmlreader import XMLReader
import helpers
from math import sqrt

import pose
import simobject
from quadtree import QuadTree, Rect

PAUSE = 0
RUN = 1

class Simulator(threading.Thread):
    """Thread that manages simobjects and their collisions, updates, and drawing routines along with supervisor updates."""
    
    nice_colors = [0x55AAEE, 0x66BB22, 0xFFBB22, 0xCC66AA,
                   0x77CCAA, 0xFF7711, 0xFF5555, 0x55CC88]

    def __init__(self, renderer, in_queue):
        """
        The viewer object supplies:
            a Renderer (viewer.renderer),
            a threading.Lock (viewer.lock) to lock painting
        and a threading.Event (viewer.event) to signal the end of painting
        """
        super(Simulator, self).__init__()

        #Attributes
        self.__stop = False
        self.__state = PAUSE
        self._renderer = renderer
        self.__center_on_robot = False
        self.__orient_on_robot = False
        self.__show_sensors = True
        self.__show_tracks = True
        
        self._in_queue = in_queue
        self._out_queue = queue.Queue()

        # Zoom on scene - Move to read_config later
        self.__time_multiplier = 1.0
        self.__time = 0.0

        # World objects
        self._robots = []
        self._trackers = []
        self._obstacles = []
        self._supervisors = []
        self._background = []
        self._zoom_default = 1

        self._world = None
        
        # Internal objects
        self.__qtree = None

    #def __delete__(self):
        #self.__state = PAUSE
        #self.__stop = True
        #self._render_lock.acquire()
        #self._render_lock.release()

    def read_config(self, config):
        ''' Read in the objects from the XML configuration file '''

        print 'reading initial configuration'
        try:
            self._world = XMLReader(config, 'simulation').read()
        except Exception, e:
            raise Exception('[Simulator.read_config] Failed to parse ' + config \
                + ': ' + str(e))
        else:
            self.__supervisor_param_cache = None
            self.__center_on_robot = False
            self.construct_world()

    def construct_world(self):
        """Creates objects from the xml settings configuration file"""
        if self._world is None:
            return

        helpers.unload_user_modules()
            
        self._robots = []
        self._obstacles = []
        self._supervisors = []
        self._background = []
        self._trackers = []
        self.__qtree = None
        
        for thing in self._world:
            thing_type = thing[0]
            if thing_type == 'robot':
                robot_type, supervisor_type, robot_pose, robot_color  = thing[1:5]
                try:
                    robot_module, robot_class = helpers.load_by_name(robot_type,'robots')
                    robot = robot_class(pose.Pose(robot_pose))
                    if robot_color is not None:
                        robot.set_color(robot_color)
                    elif len(self._robots) < 8:
                        robot.set_color(self.nice_colors[len(self._robots)])
                    sup_module, sup_class = helpers.load_by_name(supervisor_type,'supervisors')
                    supervisor = sup_class(robot.get_pose(),
                                           robot.get_info())
                    name = "Robot {}: {}".format(len(self._robots)+1, sup_class.__name__)
                    if self.__supervisor_param_cache is not None:
                        supervisor.set_parameters(self.__supervisor_param_cache[len(self._supervisors)])
                    self._out_queue.put(("make_param_window",
                                            (robot, name,
                                             supervisor.get_ui_description())))
                    self._supervisors.append(supervisor)
                    # append robot after supervisor for the case of exceptions
                    self._robots.append(robot)
                    self._trackers.append(simobject.Path(robot.get_pose(),robot))
                    self._trackers[-1].set_color(robot.get_color())
                except:
                    print "[Simulator.construct_world] Robot creation failed!"
                    raise
                    #raise Exception('[Simulator.construct_world] Unknown robot type!')
            elif thing_type == 'obstacle':
                obstacle_pose, obstacle_coords, obstacle_color = thing[1:4]
                if obstacle_color is None:
                    obstacle_color = 0xFF0000
                self._obstacles.append(
                    simobject.Polygon(pose.Pose(obstacle_pose),
                                      obstacle_coords,
                                      obstacle_color))
            elif thing_type == 'marker':
                obj_pose, obj_coords, obj_color = thing[1:4]
                if obj_color is None:
                    obj_color = 0x00FF00
                self._background.append(
                    simobject.Polygon(pose.Pose(obj_pose),
                                      obj_coords,
                                      obj_color))
            else:
                raise Exception('[Simulator.construct_world] Unknown object: '
                                + str(thing_type))
                                
        self.__time = 0.0
        if not self._robots:
            raise Exception('[Simulator.construct_world] No robot specified!')
        else:
            self.recalculate_default_zoom()
            if not self.__center_on_robot:
                self.focus_on_world()
            self.draw()
            self.__supervisor_param_cache = None

    def recalculate_default_zoom(self):
        maxsize = 0
        for robot in self._robots:
            xmin, ymin, xmax, ymax = robot.get_bounds()
            maxsize = max(maxsize,sqrt(float(xmax-xmin)**2 + float(ymax-ymin)**2))
        if maxsize == 0:
            self._zoom_default = 1
        else:
            self._zoom_default = max(self._renderer.size)/maxsize/10
            
    def reset_world(self):
        """Resets the world and objects to starting position"""
        if self._world is None:
            return
        self.__supervisor_param_cache = [sv.get_parameters() for sv in self._supervisors ]
        self.construct_world()

    def run(self):
        print 'starting simulator thread'

        time_constant = 0.02 # 20 milliseconds
        
        self._renderer.clear_screen() #create a white screen
        self.update_view()

        while not self.__stop:

            sleep(time_constant/self.__time_multiplier)

            if self.__state == RUN:

                for i, supervisor in enumerate(self._supervisors):
                    info = self._robots[i].get_info()
                    inputs = supervisor.execute( info, time_constant)
                    self._robots[i].set_inputs(inputs)

                self.__time += time_constant

                for i, robot in enumerate(self._robots):
                    robot.move(time_constant)
                    self._trackers[i].add_point(robot.get_pose())

                # the parameters that might have been changed have no effect
                # on collisions
                if self.check_collisions():
                    print "Collision detected!"
                    self.__state = PAUSE
                    #self.__stop = True

            # Draw to buffer-bitmap
            self.draw()

    def draw(self):
        """Draws the world and items in it."""
        self.process_queue()

        if self._robots and self.__center_on_robot:
            # Temporary fix - center onto first robot
            robot = self._robots[0]
            if self.__orient_on_robot:
                self._renderer.set_screen_center_pose(robot.get_pose())
            else:
                self._renderer.set_screen_center_pose(pose.Pose(robot.get_pose().x, robot.get_pose().y, 0.0))

        self._renderer.clear_screen()

        for bg_object in self._background:
            bg_object.draw(self._renderer)
        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)

        # Draw the robots, trackers and sensors after obstacles
        if self.__show_tracks:
            for tracker in self._trackers:
                tracker.draw(self._renderer)
        for robot in self._robots:
            robot.draw(self._renderer)
            if self.__show_sensors:
                robot.draw_sensors(self._renderer)

        # update view
        self.update_view()

    def update_view(self):
        self._out_queue.put(('update_view',()))
        self._out_queue.join() # wait until drawn
        
    def focus_on_world(self):
        """Centers the world on the drawing rectangle"""
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
        bounds = self._robots[0].get_bounds()
        for robot in self._robots:
            bounds = include_bounds(bounds, bloat_bounds(robot.get_bounds(),4))
        for obstacle in self._obstacles:
            bounds = include_bounds(bounds, obstacle.get_bounds())
        xl, yb, xr, yt = bounds
        self._renderer.set_view_rect(xl,yb,xr-xl,yt-yb)

    def focus_on_robot(self, rotate = True):
        """Centers the view on the robot"""
        self.__center_on_robot = True
        self.__orient_on_robot = rotate

    def show_sensors(self, show = True):
        self.__show_sensors = show

    def show_tracks(self, show = True):
        """Show tracks for every robot on simulator view"""
        self.__show_tracks = show

    def show_grid(self, show=True):
        """Show gridlines on simulator view"""
        self._renderer.show_grid(show)

    def adjust_zoom(self,factor):
        """Set the zoom by a factor. @param: factor - float"""
        self._renderer.set_zoom_level(self._zoom_default*factor)
        
    def apply_parameters(self,robot,parameters):
        """Apply some parameters to the robot"""
        # FIXME at the moment we could change parameters during calculation!
        index = self._robots.index(robot)
        if index < 0:
            print "Robot not found"
        else:
            self._supervisors[index].set_parameters(parameters)

    # Stops the thread
    def stop(self):
        """Stops the simulator thread when the entire program is closed"""
        print 'stopping simulator thread'
        self.__stop = True

    def start_simulation(self):
        """Starts the simulation"""
        if self._robots:
            self.__state = RUN
            self._out_queue.put(('simulator_running',()))

    def is_running(self):
        """A getter for simulation state"""
        return self.__state == RUN

    def pause_simulation(self):
        """pauses the simulation"""
        self.__state = PAUSE
        self._out_queue.put(('simulator_stopped',()))

    def reset_simulation(self):
        """resets the simulation to the start position"""
        self.pause_simulation()
        self.reset_world()

    def set_time_multiplier(self,multiplier):
        """"sets the time multiplier for speeding up simulation"""
        self.__time_multiplier = multiplier

    def get_time(self):
        """get the present time from the time counter for display on the UI"""
        return self.__time

    def check_collisions(self):
        """updates proximity sensors and detects collisions between objects"""
        
        collisions = []
        checked_robots = []
        
        if self.__qtree is None:
            self.__qtree = QuadTree(self._obstacles)
            
        if len(self._robots) > 1:
            rqtree = QuadTree(self._robots)
        else: rqtree = None
        
        # check each robot
        for robot in self._robots:
                
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

    def process_queue(self):
        while not self._in_queue.empty():
            tpl = self._in_queue.get()
            if isinstance(tpl,tuple) and len(tpl) == 2:
                name, args = tpl
                if name in self.__class__.__dict__:
                    try:
                        self.__class__.__dict__[name](self,*args)
                    except TypeError:
                        print "Wrong simulator event parameters {}{}".format(name,args)
                        raise
                else:
                    print "Unknown simulator event '{}'".format(name)
            else:
                print "Wrong simulator event format '{}'".format(tpl)
            self._in_queue.task_done()
    
#end class Simulator
