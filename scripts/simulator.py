"""Simulator Thread

"""
import threading
from time import sleep
from xmlparser import XMLParser

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
        #self._id = id_
        self.__state = PAUSE
        self._renderer = renderer
        self.updateView = update_callback
        self.__center_on_robot = False

        # Zoom on scene - Move to read_config later
        #self._renderer.set_zoom(130)
        self._renderer.set_screen_pose(pose.Pose(-1.6,-1.5,0))

        # World objects
        self._robots = []
        self._obstacles = []

        #test code
#        self._robots = [ khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0)), ]
#        self._robots[0].set_wheel_speeds(18,16)
#        self._obstacles = [
#            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
#            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
#            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
#            ]
        #end test code
#        self._robot = None
#        self._obstacles = []

    def read_config(self, config):
        ''' Read in the objects from the XML configuration file '''

        print 'reading initial configuration'
        parser = XMLParser(config)
        world = parser.parse()
        self._robots = []
        self._obstacles = []
        for thing in world:
            thing_type = thing[0]
            if thing_type == 'robot':
                robot_type, robot_pose  = thing[1], thing[2] 
                if robot_type == 'khepera3.K3Supervisor':
                    self._robots.append(khepera3.Khepera3(pose.Pose(robot_pose)))
                else:
                    raise Exception('[Simulator.__init__] Unknown robot type!')
            elif thing_type == 'obstacle':
                obstacle_pose, obstacle_coords = thing[1], thing[2]
                self._obstacles.append(
                    simobject.Polygon(pose.Pose(obstacle_pose),
                                      obstacle_coords,
                                      0xFF0000))
            else:
                raise Exception('[Simulator.__init__] Unknown object: ' 
                                + str(thing_type))
        
        if self._robots == None:
            raise Exception('[Simulator.__init__] No robot specified!')
        else:
            self.draw()
        self.focus_on_world()
        self.draw() # Draw at least once to show the user it has loaded

    def run(self):
        print 'starting simulator thread'

        time_constant = 0.1  # 100 milliseconds
        
        self._renderer.clear_screen() #create a white screen
        self.updateView()

        #self.draw() # Draw at least once (Move to open afterwards)
        while not self.__stop:
            sleep(time_constant)
            if self.__state != RUN:
                continue
            for robot in self._robots:
                robot.move_to(robot.pose_after(time_constant))
            # Draw to buffer-bitmap
            self.draw()
            
            if self.check_collisions():
                print "Collision detected!"
                self.__stop = True

    def draw(self):
        #Test code
        #  
        if (len(self._robots) > 0):
            # Temporary fix - center onto first robot
            robot = self._robots[0]
            self._renderer.set_screen_center_pose(robot.get_pose())

        if self.__center_on_robot:
            self._renderer.set_screen_center_pose(self._robots[0].get_pose())

        self._renderer.clear_screen()

        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)

        # Draw the robots and sensors after obstacles
        for robot in self._robots:
            robot.draw(self._renderer)
            for s in robot.ir_sensors:
                s.draw(self._renderer)
        #end test code

        self.updateView()

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
        self._renderer.set_view_rect(xl,yb,xr-xl,yt-yb)
    
    def focus_on_robot(self):
        self.__center_on_robot = True
    
    def show_grid(self, show=True):
        self._renderer.show_grid(show)
        if self._robots[0] is not None and self.__state != RUN:
            self.draw()
        
    def adjust_zoom(self,factor):
        self._renderer.scale_zoom_level(factor)
    
    # Stops the thread
    def stop(self):
        print 'stopping simulator thread'
        self.__stop = True

    def start_simulation(self):
        if self._robots is not None:
            self.__state = RUN

    def pause_simulation(self):
        self.__state = PAUSE

    def reset_simulation(self):
        pass

    def check_collisions(self):
        poly_obstacles = []
        # prepare polygons for obstacles
        for obstacle in self._obstacles:
            poly = pylygon.Polygon(obstacle.get_envelope())
            x, y, theta = obstacle.get_pose().get_list()
            poly.move_ip(x, y)
            poly.rotate_ip(theta)
            poly_obstacles.append(poly)
            #print "Obstacle:", poly
        
        poly_robots = []
        # prepare polygons for robots
        for robot in self._robots:
            points = [(x,y) for x,y,t in robot.get_envelope()]
            poly = pylygon.Polygon(points)
            x, y, theta = robot.get_pose().get_list()
            poly.move_ip(x, y)
            poly.rotate_ip(theta)
            poly_robots.append(poly)
            #print "Robot:", poly
            
        checked_robots = []
            
        # check each robot's polygon
        for robot in poly_robots:
            # against obstacles
            for obstacle in poly_obstacles:
                collisions = robot.collidepoly(obstacle)
                # collidepoly returns False value or
                # an array of projections if found
                if not collisions is False:
                    return True
                
            # against other robots
            for other in poly_robots: 
                if other == robot: continue
                if other in checked_robots: continue
                collisions = robot.collidepoly(other)
                if not collisions is False:
                    return True
            
            checked_robots.append(robot)
        return False

#end class Simulator
