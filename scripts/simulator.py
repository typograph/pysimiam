"""Simulator Thread

"""
import pysimiam
import threading
import wx
from time import sleep

import khepera3
import pose
import simobject

PAUSE = 0
RUN = 1

mEVT_VIEWER_EVENT = wx.NewEventType()
EVT_VIEWER_EVENT = wx.PyEventBinder(mEVT_VIEWER_EVENT, 1)
# Custom Event class for simulator notifications
class ViewerEvent(wx.PyCommandEvent):
    def __init__(self, index=0, id=0):
        """Constructor
        @param index - int describing index of image
        in buffer to draw to screen
        """
        evttype = mEVT_VIEWER_EVENT
        wx.PyCommandEvent.__init__(self, evttype, id)
        self.index = None

    def setIndex(self, ind):
        self.index = ind

    def getIndex(self):
        return self.index
# end class ViewerEvent

class Simulator(threading.Thread):

    def __init__(self, targetwin, renderer, id):
        super(Simulator, self).__init__()

        #Attributes
        self._id = id
        self._targetwin = targetwin
        self._stop = False
        self._state = PAUSE
        self._renderer = renderer

        #test code
        self._robot = khepera3.Khepera3(pose.Pose(200.0, 250.0, 0.0))
        self._robot.setWheelSpeeds(16,18)
        self._obstacles = [
            simobject.Polygon(pose.Pose(200,200,0),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(300,100,0.1),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000),
            simobject.Polygon(pose.Pose(100,300,0.4),[(-10,0),(0,-10),(10,0),(0,10)],0xFF0000)
            ]
        #end test code

    def run(self):
        print 'starting simulator thread'
        time_constant = 0.1
        while not self._stop:
            if self._state == RUN:
                pass

            sleep(time_constant) # 100 milliseconds

            self.robot.moveTo(self.robot.poseAfter(time_constant))

            # Post Redraw Event to UI
            if(self._targetwin):
                # Draw to buffer-bitmap
                self.draw()

                # Create UI Event
                event = ViewerEvent()
                wx.PostEvent(self._targetwin, event)

    def draw(self):
        #Test code
        self._renderer.clearScreen()
        self._robot.draw(self.renderer)
        for obstacle in self._obstacles:
            obstacle.draw(self._renderer)
        #end test code

    # Stops the thread
    def Stop(self):
        print 'stopping simulator thread'
        self.stop = True

    def start_simulation(self):
        self.state = RUN

    def pause_simulation(self):
        self.state = PAUSE

    def reset_simulation(self):
        pass


#end class Simulator
