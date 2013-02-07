"""Simulator Thread

"""
import threading
from time import sleep

import khepera3
import pose
import simobject

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
        self._robot = khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0))
        self._robot.set_wheel_speeds(18,16)
        self._obstacles = [
            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
            ]
        #end test code

    def run(self):
        print 'starting simulator thread'

        time_constant = 0.1  # 100 milliseconds
        
        self.draw() # Draw at least once (Move to open afterwards)
        
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
