"""Simulator Thread

"""
import threading
from time import sleep

import khepera3
import pose
import simobject
from xmlparser import XMLParser

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
        self.state = PAUSE
        self._renderer = renderer
        self.updateView = update_callback
        self.__center_on_robot = False
        
        self._robot = None
        self._obstacles = []

    def read_config(self, config):
        ''' Read in the objects from the XML configuration file '''

        print 'reading initial configuration'
        parser = XMLParser(config)
        world = parser.parse()
        self._robot = None
        self._obstacles = []
        for thing in world:
            thing_type = thing[0]
            if thing_type == 'robot':
                robot_type, robot_pose  = thing[1], thing[2] 
                if robot_type == 'khepera3.K3Supervisor':
                    self._robot = khepera3.Khepera3(pose.Pose(robot_pose))
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
        
        if self._robot == None:
            raise Exception('[Simulator.__init__] No robot specified!')

        self.focus_on_world()

        self.draw() # Draw at least once to show the user it has loaded


    def run(self):
        print 'starting simulator thread'

        time_constant = 0.1  # 100 milliseconds       
        
        while not self.__stop:
            sleep(time_constant)
            if self.state != RUN:
                continue
            self._robot.move_to(self._robot.pose_after(time_constant))
            # Draw to buffer-bitmap
            self.draw()

    def draw(self):
       
        if self.__center_on_robot:
            self._renderer.set_screen_center_pose(self._robot.get_pose())

        self._renderer.clear_screen()

        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)

        # Draw the robot and sensors after obstacles
        self._robot.draw(self._renderer)
        for s in self._robot.ir_sensors:
            s.draw(self._renderer)
        
        self.updateView()

    def focus_on_world(self):
        self.__center_on_robot = False
        xl, yb, xr, yt = self._robot.get_bounds()
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
        if self._robot is not None and self.state != RUN:
            self.draw()
        
    def adjust_zoom(self,factor):
        self._renderer.scale_zoom_level(factor)
    
    # Stops the thread
    def stop(self):
        print 'stopping simulator thread'
        self.__stop = True

    def start_simulation(self):
        if self._robot is not None:
            self.state = RUN

    def pause_simulation(self):
        self.state = PAUSE

    def reset_simulation(self):
        pass


#end class Simulator
