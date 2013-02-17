"""Simulator Thread
"""
import threading
from time import sleep, clock
from xmlreader import XMLReader
import helpers

import pose
import simobject
from quadtree import QuadTree, Rect

PAUSE = 0
RUN = 1

class Simulator(threading.Thread):
    """Thread that manages simobjects and their collisions, updates, and drawing routines along with supervisor updates."""
    
    nice_colors = [0x55AAEE, 0x66BB22, 0xFFBB22, 0xCC66AA,
                   0x77CCAA, 0xFF7711, 0xFF5555, 0x55CC88]

    def __init__(self, renderer, update_callback, param_callback):
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
        self.updateView = update_callback
        self.make_param_ui = param_callback
        self.__center_on_robot = False

        # Zoom on scene - Move to read_config later
        self.__time_multiplier = 1.0
        self.__time = 0.0

        self._render_lock = threading.Lock()

        # World objects
        self._robots = []
        self._trackers = []
        self._obstacles = []
        self._supervisors = []
        self._background = []

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

        self._render_lock.acquire()
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
                    self.make_param_ui(robot, name, supervisor.get_ui_description())
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
                                
        self._render_lock.release()
        self.__time = 0.0
        if not self._robots:
            raise Exception('[Simulator.construct_world] No robot specified!')
        else:
            if not self.__center_on_robot:
                self.focus_on_world()
            self.draw()
            self.__supervisor_param_cache = None

    def reset_world(self):
        """Resets the world and objects to starting position"""
        if self._world is None:
            return
        self.__supervisor_param_cache = [sv.get_parameters() for sv in self._supervisors ]
        self.construct_world()

    def run(self):
        print 'starting simulator thread'

        time_constant = 0.02  # 20 milliseconds
        
        self._render_lock.acquire()
        self._renderer.clear_screen() #create a white screen
        self.updateView()
        self._render_lock.release()

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

                if self.check_collisions():
                    print "Collision detected!"
                    self.__state = PAUSE
                    #self.__stop = True
                #self.update_sensors()

            # Draw to buffer-bitmap
            self.draw()

    def draw(self):
        """Draws the world and items in it."""
        self._render_lock.acquire()
        if self._robots and self.__center_on_robot:
            # Temporary fix - center onto first robot
            robot = self._robots[0]
            self._renderer.set_screen_center_pose(robot.get_pose())

        self._renderer.clear_screen()

        for bg_object in self._background:
            bg_object.draw(self._renderer)
        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)

        # Draw the robots, trackers and sensors after obstacles
        for tracker in self._trackers:
            tracker.draw(self._renderer)
        for robot in self._robots:
            robot.draw(self._renderer)
            robot.draw_sensors(self._renderer)

        self.updateView()
        self._render_lock.release()

    def focus_on_world(self):
        """Centers the world on the drawing rectangle"""
        self.__center_on_robot = False
        xl, yb, xr, yt = self._robots[0].get_bounds()
        for obstacle in self._obstacles:
            xlo, ybo, xro, yto = obstacle.get_bounds()
            if xlo < xl:
                xl = xlo
            if xro > xr:
                xr = xro
            if ybo < yb:
                yb = ybo
            if yto > yt:
                yt = yto
        self._render_lock.acquire()
        self._renderer.set_view_rect(xl,yb,xr-xl,yt-yb)
        self._render_lock.release()

    def focus_on_robot(self):
        """Centers the view on the robot"""
        self._render_lock.acquire()
        self.__center_on_robot = True
        self._render_lock.release()

    def show_grid(self, show=True):
        """Show gridlines on simulator view"""
        self._render_lock.acquire()
        self._renderer.show_grid(show)
        self._render_lock.release()
        if self._robots[0] is not None and self.__state != RUN:
            self.draw()

    def adjust_zoom(self,factor):
        """Set the zoom by a factor. @param: factor - float"""
        self._render_lock.acquire()
        self._renderer.scale_zoom_level(factor)
        self._render_lock.release()
        
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

    def is_running(self):
        """A getter for simulation state"""
        return self.__state == RUN

    def pause_simulation(self):
        """pauses the simulation"""
        self.__state = PAUSE

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
        ''' Detect collisions between objects '''
        
        collisions = []
        checked_robots = []
        
        if self.__qtree is None:
            self.__qtree = QuadTree(self._obstacles)
        
        # check each robot
        for robot in self._robots:
                
            # update proximity sensors
            for sensor in robot.get_external_sensors():
                sensor.get_world_envelope(True)
                rect = Rect(sensor.get_bounding_rect())
                sensor.update_distance()
                for obstacle in self.__qtree.find_items(rect):
                    if (sensor.update_distance(obstacle)):
                        print "{0} -> {1} Distance:{2}".format(
                                sensor, obstacle, sensor.distance())
            
            rect = Rect(robot.get_bounding_rect())
            
            # against nearest obstacles
            for obstacle in self.__qtree.find_items(rect):
                # Test Code: print "In proximity to:", obstacle
                if robot.has_collision(obstacle):
                    collisions.append((robot, obstacle))
            
            # against other robots
            for other in self._robots: 
                if other is robot: continue
                #TODO: robot.update_sensors(other)
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

    
    def update_sensors(self):
        ''' Update robot's sensors '''
        # Depricated 
        return
        
#end class Simulator
