import wx

import gui

class MainWindow(wx.Frame):
    def __init__(self, mainpanel=None):
        wx.Frame.__init__(self, None, title="PiVT Desktop", size=(600,400))
        self.mainpanel = mainpanel
        self.SetupMenus()
             
    def SetupMenus(self):
        # File Menu
        filemenu = wx.Menu()
        menuItem = filemenu.Append(wx.ID_OPEN, "&Open Playlist...")
        self.Bind(wx.EVT_MENU, self.OnOpen, menuItem)
        menuItem = filemenu.Append(wx.ID_SAVE, "&Save Playlist")
        self.Bind(wx.EVT_MENU, self.OnSave, menuItem)
        filemenu.Enable(wx.ID_SAVE, False)
        menuItem = filemenu.Append(wx.ID_SAVEAS, "Save Playlist &as...")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menuItem)
        menuItem = filemenu.Append(wx.ID_EXIT, "E&xit", " Close the program")
        self.Bind(wx.EVT_MENU, self.OnExit, menuItem)
        
        # Connection Menu
        connectmenu = wx.Menu()
        menuItem = connectmenu.Append(wx.ID_ANY, "&Connect")
        self.Bind(wx.EVT_MENU, self.OnConnectInstruction, menuItem)
        menuItem = connectmenu.Append(wx.ID_ANY, "&Disconnect")
        self.Bind(wx.EVT_MENU, self.OnDisconnectInstruction, menuItem)
        connectmenu.Enable(menuItem.GetId(), False)
        menuItem = connectmenu.Append(wx.ID_ANY, "Connection &Options...")
        self.Bind(wx.EVT_MENU, self.OnConnectOptions, menuItem)
        
        # Help Menu
        helpmenu = wx.Menu()
        menuItem = helpmenu.Append(wx.ID_HELP, "&Help...")
        self.Bind(wx.EVT_MENU, self.OnHelp, menuItem)
        
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(connectmenu, "&Connection")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        
    def OnOpen(self, event):
        pass
    def OnSave(self, event):
        pass
    def OnSaveAs(self, event):
        pass
    def OnExit(self, event):
        self.Close(True)
        
    def OnConnectInstruction(self, event):
        
        self.mainpanel.lblPlaying.SetLabel("Test2")
        pass
    def OnDisconnectInstruction(self, event):
        pass
    def OnConnectOptions(self, event):
        pass
    
    def OnHelp(self, event):
        pass


class MainPanel(gui.CorePanel):
    def __init__(self, parent): 
        gui.CorePanel.__init__(self, parent)       
    def OnMoveUp(self, event):
        self.lblPlaying.SetLabel("Test")
    def OnSave(self, event):
        pass
    def OnSaveAs(self, event):
        pass
    def OnExit(self, event):
        self.Close(True)

    def OnConnectInstruction(self, event):
        pass
    def OnDisconnectInstruction(self, event):
        pass
    def OnConnectOptions(self, event):
        pass
    
    def OnHelp(self, event):
        pass
    

app = wx.App(False)
frame = MainWindow()
panel = MainPanel(frame)
frame.mainpanel = panel
frame.Show()
app.MainLoop() 