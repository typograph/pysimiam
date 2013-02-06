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
        self.renderer = renderer
        self.updateView = update_callback
        
        #test code
        self.robot = khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0))
        self.robot.setWheelSpeeds(18,16)
        self.obstacles = [
            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
            ]
        #end test code

    def run(self):
        print 'starting simulator thread'
        time_constant = 0.1  # 100 milliseconds
        while not self.__stop:
            if self.state == RUN:
                pass    
            
            sleep(time_constant)

            self.robot.moveTo(self.robot.poseAfter(time_constant))
            
            # Draw to buffer-bitmap
            self.draw()


    def draw(self):
       
        #Test code
        self.renderer.clearScreen()
        self.robot.draw(self.renderer)
        for obstacle in self.obstacles:
            obstacle.draw(self.renderer)
        #end test code
        
        self.updateView()
        
    # Stops the thread
    def stop(self):
        print 'stopping simulator thread'
        self.__stop = True

    def startSimulation(self):
        self.state = RUN

    def pauseSimulation(self):
        self.state = PAUSE

    def resetSimulation(self):
        pass

        
#end class Simulator
