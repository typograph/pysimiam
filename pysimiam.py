import wx
import os

class PySimiamApp(wx.App):
	def OnInit(self):
		self.frame = PySimiamFrame(None, size=wx.Size(800,600), title="PySimiam")
		self.SetTopWindow(self.frame)
		self.frame.Show()

		return True

#end PySimiamApp class

class PySimiamFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        #Objects

        #Interface buttons
        # Reset
        path = os.path.abspath("./res/image/arrow-left-double.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self.resetButton = wx.BitmapButton(self, id=wx.ID_ANY, \
                bitmap=bmp, size=(32,32))

        # Play
        path = os.path.abspath("./res/image/arrow-right.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self.playButton = wx.BitmapButton(self, id=wx.ID_ANY, \
                bitmap=bmp, size=(32, 32))

        # Pause
        path = os.path.abspath("./res/image/media-playback-pause-7.png")
        bmp = wx.Bitmap(path, wx.BITMAP_TYPE_PNG)
        self.pauseButton = wx.BitmapButton(self, id=wx.ID_ANY, \
                bitmap=bmp, size=(32, 32))


        # Simulation Panel (now just a text placeholder)
        self.simulator = wx.Panel(self)
        self.simulator.SetBackgroundColour('grey')

        wx.StaticText(self.simulator, label="hello")

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

        #Layout Simulator
        mainSizer.Add(self.simulator, 1, wx.EXPAND|wx.ALIGN_CENTER|wx.ALL, 5)

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

        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)

    def __set_properties(self):
        pass
 

    # Event Handlers

    def OnOpen(self, event):
        event.Skip()

    def OnClose(self, event):
        self.Destroy()

#end PySimiamFrame class

if __name__ == "__main__":
    #provider = wx.SimpleHelpProvider()
    #wx.HelpProvider_Set(provider)
    app = PySimiamApp(False)
    app.MainLoop()
