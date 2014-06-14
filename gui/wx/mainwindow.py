"""PySimiam
Description: This is the top-level application for PySimiam.
"""
import sys
sys.path.insert(0, './scripts')
import wx
import os
import wx.lib.newevent
from .renderer import wxGCRenderer

import core.simulator as sim
import threading

class PySimiamApp(wx.App):
    def OnInit(self):
        self.frame = PySimiamFrame(None,
                                   size = wx.Size(BITMAP_WIDTH, BITMAP_HEIGHT),
                                   title = "PySimiam")
        self.SetTopWindow(self.frame)
        self.frame.Show()

        return True

#end PySimiamApp class

# Create any event IDs that may be needed
ID_OPEN_XML = wx.NewId()
ID_PLAY = wx.NewId()
ID_PAUSE = wx.NewId()
ID_RESET = wx.NewId()

BITMAP_WIDTH = 400
BITMAP_HEIGHT = 400

class PySimiamFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        #Objects

        #Interface buttons
        # Reset
        path = os.path.abspath("./res/image/arrow-left-double.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self._reset_button = wx.BitmapButton(self, id=ID_RESET, \
                bitmap=bmp, size=(32,32))

        # Play
        path = os.path.abspath("./res/image/arrow-right.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self._play_button = wx.BitmapButton(self, id=ID_PLAY, \
                bitmap=bmp, size=(32, 32))

        # Pause
        path = os.path.abspath("./res/image/media-playback-pause-7.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self._pause_button = wx.BitmapButton(self, id=ID_PAUSE, \
                bitmap=bmp, size=(32, 32))


        # Simulation Panel
        self._viewer = SimulatorViewerPanel(self)
        # create the simulator thread
        self._simulator_thread = sim.Simulator(self._viewer.renderer,
                                               self._viewer.update_bitmap)
        
        # start simulator thread
        self._simulator_thread.start()

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
        buttonSizer.Add(self._reset_button, 0, wx.ALL, 2)
        buttonSizer.Add(self._play_button, 0, wx.ALL, 2)
        buttonSizer.Add(self._pause_button, 0, wx.ALL, 2)
        mainSizer.Add(buttonSizer, 0, wx.EXPAND)

        ##Create scrolling area
        scroller = wx.ScrolledWindow(self)
        scroller.SetScrollbars(1,1,1,1)
        self._viewer.Reparent(scroller)
        sizer = wx.BoxSizer()
        sizer.Add(self._viewer, 1, wx.EXPAND)
        scroller.SetSizer(sizer)

        # Layout Simulator
        mainSizer.Add(scroller, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)

        # Set 'mainsizer' as the sizer for the frame
        self.SetSizer(mainSizer)

    def __create_toolbars(self):
        #MenuBar
        self._menu_bar = wx.MenuBar()
        self._filem = wx.Menu()
        self._filem.Append(ID_OPEN_XML, "Open XML World\tCtrl+W")
        self._filem.Append(wx.ID_OPEN, "Open Supervisor\tCtrl+O")
        self._filem.AppendSeparator()

        self._filem.Append(wx.ID_CLOSE, "Exit", "Quit the Program" )
        self._menu_bar.Append(self._filem, "&File")
        self.SetMenuBar(self._menu_bar)

        self.Bind(wx.EVT_MENU, self._on_close, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self._on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self._on_open_world, id=ID_OPEN_XML)

    def __set_properties(self):
        self.Bind(wx.EVT_BUTTON, self._on_button, id=wx.ID_ANY)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        #self.Bind(sim.EVT_VIEWER_EVENT, self._update_viewer)

    # Methods

    # Event Handlers
    def _update_viewer(self, event):
        #paint bitmap to panel
        self._viewer.paint_now(self._bitmap)

    def _on_button(self, event):
        event_id = event.GetId()
        if event_id == ID_PLAY:
            self._simulator_thread.start_simulation()
        elif event_id == ID_PAUSE:
            self._simulator_thread.pause_simulation()
        elif event_id == ID_RESET:
            self._simulator_thread.reset_simulation()
        else:
            print('ButtonPress: unknown')

        event.Skip()
        #End _on_button

    def _on_open(self, event):
        wildcard = "Supervisor(*.py)|*.py|"
        dlg = wx.FileDialog(
            self, message="Select Supervisor.py File",
            defaultDir="supervisors", 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            ) 

        res = dlg.ShowModal()
        if (res == wx.ID_OK):
            print('hi')

        dlg.Destroy()

        event.Skip()
        #End _on_open

    def _on_open_world(self, event):
        wildcard = "WorldFile(*.xml)|*.xml|"
        dlg = wx.FileDialog(
            self, message="Select World.xml File",
            defaultDir="worlds", 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            ) 

        res = dlg.ShowModal()
        if (res == wx.ID_OK):
            self._simulator_thread.read_config(dlg.GetPath())
        dlg.Destroy()
        event.Skip()

    def _on_close(self, event):
        # Stop simulator thread
        self._simulator_thread.stop()
        self._simulator_thread.join()
        self.Destroy()
        #End onClose

#end PySimiamFrame class

class SimulatorViewerPanel(wx.Panel):
    def __init__(self, parent):
        super(SimulatorViewerPanel, self).__init__(parent)

        # Create bitmaps and contexts
        self.__bitmap = wx.EmptyBitmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        self.__bitmap_dc = wx.MemoryDC(self.__bitmap)
        
        self.__blt_bitmap = wx.EmptyBitmap(BITMAP_WIDTH, BITMAP_HEIGHT)
        self.__blt_bitmap_dc = wx.MemoryDC(self.__blt_bitmap)
        
        self.renderer = wxGCRenderer(self.__blt_bitmap_dc)
        self.lock = threading.Lock()
        
        self.Bind(wx.EVT_PAINT, self._on_paint)
        

    # Methods
    def update_bitmap(self):
        self.lock.acquire()
        self.__bitmap_dc.Blit(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT,
                              self.__blt_bitmap_dc, 0, 0,
                              wx.COPY, False, 0, 0)
        self.lock.release()
        wx.CallAfter(self._paint_now,None)

    def _paint_now(self, event):
        self.lock.acquire()
        dc = wx.ClientDC(self)
        dc.Blit(0, 0, BITMAP_WIDTH, BITMAP_HEIGHT,
                self.__bitmap_dc, 0, 0,
                wx.COPY, False, 0, 0)
        self.lock.release()

    def _on_paint(self, event):
        pass
        #self.lock.acquire()
        #dc = wx.PaintDC(self)
        #dc.DrawBitmap(self.__bitmap, 0, 0, False) # no mask
        #self.lock.release()
        self.__bitmap_dc.DrawBitmap(self.__blt_bitmap, 0, 0, False) # no mask
        self.lock.release()
        wx.CallAfter(self._on_paint,None)
        

    def _on_paint(self, event):
        self.lock.acquire()
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.__bitmap, 0, 0, False) # no mask
        self.lock.release()

if __name__ == "__main__":
    #provider = wx.SimpleHelpProvider()
    #wx.HelpProvider_Set(provider)
    app = PySimiamApp(False)
    app.MainLoop()
