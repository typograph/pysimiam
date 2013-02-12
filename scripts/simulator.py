"""Simulator Thread
"""
import threading
from time import sleep, clock
from xmlparser import XMLParser
import helpers

import khepera3
import pose
import simobject
from xmlparser import XMLParser
import pylygon

PAUSE = 0
RUN = 1

class Simulator(threading.Thread):

    def __init__(self, renderer, update_callback):
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
        self.__center_on_robot = False

        # Zoom on scene - Move to read_config later
        self.__time_multiplier = 1.0
        self.__time = 0.0

        self._render_lock = threading.Lock()

        # World objects
        self._robots = []
        self._obstacles = []

        self._world = None

    #def __delete__(self):
        #self.__state = PAUSE
        #self.__stop = True
        #self._render_lock.acquire()
        #self._render_lock.release()

    def read_config(self, config):
        ''' Read in the objects from the XML configuration file '''

        print 'reading initial configuration'
        try:
            parser = XMLParser(config)
            self._world = parser.parse_simulation()
        except Exception, e:
            raise Exception('[Simulator.read_config] Failed to parse ' + config \
                + ': ' + str(e))
        else:
            self.construct_world()

    def construct_world(self):
        if self._world is None:
            return

        self._render_lock.acquire()
        self._robots = []
        self._obstacles = []
        self._supervisors = []
        for thing in self._world:
            thing_type = thing[0]
            if thing_type == 'robot':
                sup_type, robot_pose = thing[1:3]
                #FIXME uncomment the following after changes to the parser
                #robot_type, robot_pose, sup_type  = thing[1:4]
                try:
                    #FIXME uncomment the following after changes to the parser
                    #robot_module, robot_class = helpers.load_by_name(robot_type)
                    robot_module, robot_class = helpers.load_by_name("khepera3",'robots')
                    robot = robot_class(pose.Pose(robot_pose))
                    sup_module, sup_class = helpers.load_by_name(sup_type,'supervisors')
                    self._supervisors.append(sup_class(robot.get_pose(), robot.get_info()))
                    # append robot after supervisor for the case of exceptions
                    self._robots.append(robot)
                except:
                    raise
                    #raise Exception('[Simulator.__init__] Unknown robot type!')
            elif thing_type == 'obstacle':
                obstacle_pose, obstacle_coords = thing[1], thing[2]
                self._obstacles.append(
                    simobject.Polygon(pose.Pose(obstacle_pose),
                                      obstacle_coords,
                                      0xFF0000))
            else:
                raise Exception('[Simulator.__init__] Unknown object: '
                                + str(thing_type))
                                
        self._render_lock.release()
        self.__time = 0.0
        if not self._robots:
            raise Exception('[Simulator.__init__] No robot specified!')
        else:
            self.focus_on_world()
            self.draw()

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

                for robot in self._robots:
                    robot.move(time_constant)

                if self.check_collisions():
                    print "Collision detected!"
                    self.__state = PAUSE
                    #self.__stop = True

            # Draw to buffer-bitmap
            self.draw()


    def draw(self):
        self._render_lock.acquire()
        if self._robots and self.__center_on_robot:
            # Temporary fix - center onto first robot
            robot = self._robots[0]
            self._renderer.set_screen_center_pose(robot.get_pose())

        self._renderer.clear_screen()

        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)

        # Draw the robots and sensors after obstacles
        for robot in self._robots:
            robot.draw(self._renderer)
            for s in robot.ir_sensors:
                s.draw(self._renderer)

        self.updateView()
        self._render_lock.release()

    def focus_on_world(self):
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
        self._render_lock.acquire()
        self.__center_on_robot = True
        self._render_lock.release()

    def show_grid(self, show=True):
        self._render_lock.acquire()
        self._renderer.show_grid(show)
        self._render_lock.release()
        if self._robots[0] is not None and self.__state != RUN:
            self.draw()

    def adjust_zoom(self,factor):
        self._render_lock.acquire()
        self._renderer.scale_zoom_level(factor)
        self._render_lock.release()

    # Stops the thread
    def stop(self):
        print 'stopping simulator thread'
        self.__stop = True

    def start_simulation(self):
        if self._robots:
            self.__state = RUN

    def is_running(self):
        return self.__state == RUN

    def pause_simulation(self):
        self.__state = PAUSE

    def reset_simulation(self):
        self.pause_simulation()
        self.construct_world()

    def set_time_multiplier(self,multiplier):
        self.__time_multiplier = multiplier

    def get_time(self):
        return self.__time

    def check_collisions(self):
        ''' Detect collisions between objects '''
        scaling_factor = 1.
        poly_obstacles = []
        # prepare polygons for obstacles
        for obstacle in self._obstacles:
            points = [(x*scaling_factor, y*scaling_factor)
                      for x,y in obstacle.get_world_envelope()]
            poly = pylygon.Polygon(points)
            poly_obstacles.append(poly)

        poly_robots = []
        # prepare polygons for robots
        for robot in self._robots:
            points = [(x*scaling_factor, y*scaling_factor)
                      for x,y in robot.get_world_envelope()]
            poly = pylygon.Polygon(points)
            poly_robots.append(poly)

        checked_robots = []

        # check each robot's polygon
        for robot in poly_robots:
            # against obstacles
            for obstacle in poly_obstacles:
                collisions = robot.collidepoly(obstacle)
                # collidepoly returns False value or
                # an array of projections if found
                if isinstance(collisions, bool):
                    if collisions == False: continue
                print "Collisions:", collisions
                print "Robot:", robot, "\nObstacle:", obstacle
                return True

            # against other robots
            for other in poly_robots:
                if other == robot: continue
                if other in checked_robots: continue
                collisions = robot.collidepoly(other)
                if isinstance(collisions, bool):
                    if collisions == False: continue
                print "Collisions:", collisions
                print "Robot1:", robot, "\nRobot2:", other
                return True
            checked_robots.append(robot)
        return False

#end class Simulator
