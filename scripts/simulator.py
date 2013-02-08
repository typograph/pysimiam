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
        self._renderer.set_zoom(2)
        
        #test code
        self._robot = None
        self._obstacles = []
        
#        self._robot = khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0))
#        self._robot.set_wheel_speeds(18,16)
#        self._obstacles = [
#            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
#            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
#            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
#            ]
        #end test code

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
        else:
            self.draw()


    def run(self):
        print 'starting simulator thread'

        time_constant = 0.1  # 100 milliseconds
        
        self._renderer.clear_screen() #create a white screen
        self.updateView()

        #self.draw() # Draw at least once (Move to open afterwards)
        while not self.__stop:
            sleep(time_constant)
            if self.state != RUN:
                continue
            self._robot.move_to(self._robot.pose_after(time_constant))
            # Draw to buffer-bitmap
            self.draw()

    def draw(self):
       
        #Test code
        self._renderer.set_screen_center_pose(self._robot.get_pose())
        self._renderer.clear_screen()
        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)
        # Draw the robot and sensors after obstacles
        self._robot.draw(self._renderer)
        for s in self._robot.ir_sensors:
            s.draw(self._renderer)
        #end test code
        
        self.updateView()
        
    # Stops the thread
    def stop(self):
        print 'stopping simulator thread'
        self.__stop = True

    def start_simulation(self):
        self.state = RUN

    def pause_simulation(self):
        self.state = PAUSE

    def reset_simulation(self):
        pass


#end class Simulator
