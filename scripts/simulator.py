"""Simulator Thread

"""
import pysimiam
import threading
import wx
from time import sleep

import khepera3
import pose
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
        
        #test code
        pos = pose.Pose(10.0, 10.0, 0.0)
        self.robot = khepera3.Khepera3(pos)
        #end test code

    def run(self):
        print 'starting simulator thread'
        imageIndex = 0
        while not self.stop:
            if self.state == RUN:
                pass    
            
            sleep(0.05) # 100 milliseconds


            
            # Post Redraw Event to UI
            if(self.targetwin):
                # Draw to buffer-bitmap
                self.draw(imageIndex)

                # Create UI Event
                event = ViewerEvent() 
                event.setIndex(self.__swapIndex(imageIndex))
                wx.PostEvent(self.targetwin, event)

            #Swap buffer index
            imageIndex = self.__swapIndex(imageIndex)

    def __swapIndex(self, ind):
        if ind == 1:
            return 0
        else:
            return 1

    def draw(self, imageIndex):
        print imageIndex
        dc = wx.MemoryDC(self.bitmaplist[imageIndex])

        #Test code
        gc = wxrenderer.wxGCRenderer(dc)
        self.robot.draw(gc)
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
