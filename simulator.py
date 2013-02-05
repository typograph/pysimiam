"""Simulator Thread

"""
import pysimiam
import threading
import wx
from time import sleep

import pose
import khepera3
import wxrenderer

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
        #wx.PyEvent.__init__(self, id, evttype)
        wx.PyCommandEvent.__init__(self, evttype, id)
        self.index = None 

    def setIndex(self, ind):
        self.index = ind

    def getIndex(self):
        return self.index
        
# end class ViewerEvent

class Simulator(threading.Thread):

    def __init__(self, targetwin, bitmaplist, id):
        super(Simulator, self).__init__()
        
        #Attributes
        self.id = id
        self.targetwin = targetwin
        self.stop = False
        self.state = PAUSE
        self.bitmaplist = bitmaplist

    def run(self):
        print 'starting simulator thread'
        #Test
        pos = pose.Pose(10.0, 10.0, 0.0) # (x,y,theta)
        robot = Khepera3(pos)

        imageIndex = 0
        while not self.stop:
            if self.state == RUN:
                #Test Mutex and post event
                pass    
            
            sleep(3) # 100 milliseconds


            # Draw to buffer-bitmap
            self.draw(imageIndex)

            # Post Redraw Event to UI
            if(self.targetwin):
                event = ViewerEvent() 
                event.setIndex(imageIndex)
                wx.PostEvent(self.targetwin, event)

            #Swap buffer index
            if imageIndex == 1:
                imageIndex = 0
            else:
                imageIndex = 1

    def draw(self, imageIndex):
        print imageIndex
        dc = wx.MemoryDC(self.bitmaplist[imageIndex])
        wxR = wxrenderer.



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
