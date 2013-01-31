import wx

class PySimianApp(wx.App):
	def OnInit(self):
		self.frame = PySimianFrame(None, size=wx.Size(800,600), title="PySimian")
		self.SetTopWindow(self.frame)
		self.frame.Show()

		return True

#end PySimianApp class

class PySimianFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        #Objects
        #self.simulator = Simulator(self)

        #Interface buttons
        #self.playButton = wx.ImageButton(self)

        # Create layouts to arrange objects
        self.__do_layout()

        # Create any drop-down menu bars and toolbars
        self.__create_toolbars()
    
        # Set any special properties of the frame
        self.__set_properties()

        # Create status bar with intro messages
        self.CreateStatusBar()
        self.PushStatusText("Welcome to PySimian") 

    def __do_layout(self):
        pass 

    def __create_toolbars(self):
        #MenuBar	
        self.menu_bar = wx.MenuBar()
        self.filem = wx.Menu()
        self.filem.Append(wx.ID_OPEN, "Open Supervisor\tCtrl+O")
        self.filem.AppendSeparator()

        #self.filem.Append(ID_QUIT, "Exit", "Quit the Program")
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

#end PySimianFrame class

if __name__ == "__main__":
    #provider = wx.SimpleHelpProvider()
    #wx.HelpProvider_Set(provider)
    app = PySimianApp(False)
    app.MainLoop()
