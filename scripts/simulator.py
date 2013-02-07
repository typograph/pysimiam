"""Simulator Thread

"""
import pysimiam
import threading
import wx
from time import sleep
from xmlparser import XMLParser

import khepera3
import pose
import simobject

PAUSE = 0
RUN = 1

mEVT_VIEWER_EVENT = wx.NewEventType()
EVT_VIEWER_EVENT = wx.PyEventBinder(mEVT_VIEWER_EVENT, 1)
# Custom Event class for simulator notifications
class ViewerEvent(wx.PyCommandEvent):
    def __init__(self, index=0, id_=0):
        """Constructor
        @param index - int describing index of image
        in buffer to draw to screen
        """
        evttype = mEVT_VIEWER_EVENT
        #wx.PyEvent.__init__(self, id_, evttype)
        wx.PyCommandEvent.__init__(self, evttype, id_)
        self.index = None 

    def setIndex(self, ind):
        self.index = ind

    def getIndex(self):
        return self.index
        
# end class ViewerEvent

class Simulator(threading.Thread):

    def __init__(self, targetwin, renderer, id_):
        super(Simulator, self).__init__()
        
        #Attributes
        self.id = id_
        self.targetwin = targetwin
        self.stop = False
        self.state = PAUSE
        self.renderer = renderer
        
        #test code
        self.robot = khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0))
        self.robot.setWheelSpeeds(16,18)
        self.obstacles = [
            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
            ]
        #end test code

    def read_config(self, config):
        ''' Read in the objects from the XML configuration file '''

        print 'reading initial configuration'
        parser = XMLParser(config)
        world = parser.parse()
        self.robot = None
        self.obstacles = []
        for thing in world:
            thing_type = thing[0]
            if thing_type == 'robot':
                robot_type, robot_pose  = thing[1], thing[2] 
                if robot_type == 'khepera3.K3Supervisor':
                    self.robot = khepera3.Khepera3(pose.Pose(robot_pose))
                else:
                    raise Exception('[Simulator.__init__] Unknown robot type!')
            elif thing_type == 'obstacle':
                obstacle_pose, obstacle_coords = thing[1], thing[2]
                self.obstacles.append(
                    simobject.Polygon(pose.Pose(obstacle_pose),
                                      obstacle_coords,
                                      0xFF0000))
            else:
                raise Exception('[Simulator.__init__] Unknown object: ' 
                                + str(thing_type))
        
        if self.robot == None:
            raise Exception('[Simulator.__init__] No robot specified!')
    
    def run(self):
        print 'starting simulator thread'
        time_constant = 0.1
        while not self.stop:
            if self.state == RUN:
                pass    
            
            sleep(time_constant) # 100 milliseconds

            self.robot.moveTo(self.robot.poseAfter(time_constant))
            
            # Post Redraw Event to UI
            if(self.targetwin):
                # Draw to buffer-bitmap
                self.draw()

                # Create UI Event
                event = ViewerEvent() 
                wx.PostEvent(self.targetwin, event)

    def draw(self):
        #Test code
        self.renderer.clearScreen()
        self.robot.draw(self.renderer)
        for obstacle in self.obstacles:
            obstacle.draw(self.renderer)
        #end test code

    # Stops the thread
    def Stop(self):
        print 'stopping simulator thread'
        self.stop = True

    def startSimulation(self):
        self.state = RUN

    def pauseSimulation(self):
        self.state = PAUSE

    def resetSimulation(self):
        pass

        
#end class Simulator
