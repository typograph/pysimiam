"""PySimiam
Author: Jonathan Whitten
ChangeDate: 2 FEB 2013; 1134EST
Description: This is the top-level application for PySimiam.
"""
import sys
sys.path.insert(0, './scripts')
import wx
import os
import wx.lib.newevent
from wxrenderer import wxGCRenderer

import simulator as sim
import threading

class PySimiamApp(wx.App):
    def OnInit(self):
        self.frame = PySimiamFrame(None, size=wx.Size(800,600), title="PySimiam")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True

#end PySimiamApp class

# Create any event IDs that may be needed
ID_PLAY = wx.NewId()
ID_PAUSE = wx.NewId()
ID_RESET = wx.NewId()

BITMAP_WIDTH = 600
BITMAP_HEIGHT = 800

class PySimiamFrame(wx.Frame):
    
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        #Objects

        #Interface buttons
        # Reset
        path = os.path.abspath("./res/image/arrow-left-double.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self.resetButton = wx.BitmapButton(self, id=ID_RESET, \
                bitmap=bmp, size=(32,32))

        # Play
        path = os.path.abspath("./res/image/arrow-right.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self.playButton = wx.BitmapButton(self, id=ID_PLAY, \
                bitmap=bmp, size=(32, 32))

        # Pause
        path = os.path.abspath("./res/image/media-playback-pause-7.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self.pauseButton = wx.BitmapButton(self, id=ID_PAUSE, \
                bitmap=bmp, size=(32, 32))


        # Simulation Panel
        viewer = SimulatorViewer(self)
        # create the simulator thread
        self.simulatorThread = sim.Simulator(viewer.renderer, viewer.updateBitmap)
        self.simulatorThread.start()


        # Create layouts to arrange objects
        self.__do_layout()

        # Create any drop-down menu bars and toolbars
        self.__create_toolbars()
    
        # Set any special properties of the frame
        self.__set_properties()

        # Create status bar with intro messages
        self.CreateStatusBar()
        self.PushStatusText("Welcome to PySimiam") 

    def __do_layout(self):
        # Create main vertical sizer 'mainsizer'
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Layout buttons
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.resetButton, 0, wx.ALL, 2)
        buttonSizer.Add(self.playButton, 0, wx.ALL, 2)
        buttonSizer.Add(self.pauseButton, 0, wx.ALL, 2)
        mainSizer.Add(buttonSizer, 0, wx.EXPAND)

        # Layout Simulator
        mainSizer.Add(self.viewer, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)

        # Set 'mainsizer' as the sizer for the frame
        self.SetSizer(mainSizer)

    def __create_toolbars(self):
        #MenuBar    
        self.menu_bar = wx.MenuBar()
        self.filem = wx.Menu()
        self.filem.Append(wx.ID_OPEN, "Open Supervisor\tCtrl+O")
        self.filem.AppendSeparator()

        self.filem.Append(wx.ID_CLOSE, "Exit", "Quit the Program" )
        self.menu_bar.Append(self.filem, "&File")
        self.SetMenuBar(self.menu_bar)

        self.Bind(wx.EVT_MENU, self.onClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.onOpen, id=wx.ID_OPEN)

    def __set_properties(self):
        self.Bind(wx.EVT_BUTTON, self.onButton, id=wx.ID_ANY) 
        self.Bind(wx.EVT_CLOSE, self.onClose)

    # Methods

    # Event Handlers
    def onButton(self, event):
        eventId = event.GetId()

        if eventId == ID_PLAY:
            print 'ButtonPress: play'
        elif eventId == ID_PAUSE:
            print 'ButtonPress: pause'
        elif eventId == ID_RESET:
            print 'ButtonPress: reset'
        else:
            print 'ButtonPress: unknown'

        event.Skip()
        #End onButton

    def onOpen(self, event):
        event.Skip()

        #End onOpen

    def onClose(self, event):
        # Stop simulator thread
        self.simulatorThread.stop()
        self.Destroy()

        #End onClose

#end PySimiamFrame class

class SimulatorViewer(wx.ScrolledWindow):
    def __init__(self, parent):
        super(SimulatorViewer, self).__init__(parent)
        self.__set_properties()
        self.__bitmap = wx.EmptyBitmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        self.__bitmap_dc = wx.MemoryDC(self.__bitmap)
        self.__blt_bitmap = wx.EmptyBitmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        self.lock = threading.Lock()
        dc = wx.MemoryDC(self.__blt_bitmap)
        self.renderer = wxGCRenderer(dc)

    def __set_properties(self):
        self.SetScrollbars(1,1,1,1)        
        self.Bind(wx.EVT_PAINT, self.onPaint)

    # Methods
    def updateBitmap(self):
        self.lock.acquire()
        self.__bitmap_dc.DrawBitmap(self.__blt_bitmap, 0, 0, False) # no mask
        self.lock.release()
        wx.CallAfter(self.onPaint,None)
        

    def onPaint(self, event):
        self.lock.acquire()
        dc = wx.ClientDC(self)
        dc.DrawBitmap(self.__bitmap, 0, 0, False) # no mask
        self.lock.release()


if __name__ == "__main__":
    #provider = wx.SimpleHelpProvider()
    #wx.HelpProvider_Set(provider)
    app = PySimiamApp(False)
    app.MainLoop()
