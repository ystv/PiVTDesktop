import wx
import os

import gui

from playlist import Playlist
from gui import dlgConnectOptions


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="PiVT Desktop", size=(600,400))
        self.mp = None
        self.SetupMenus()
             
    def SetupMenus(self):
        # File Menu
        filemenu = wx.Menu()
        menuItem = filemenu.Append(wx.ID_OPEN, "&Open Playlist...")
        self.Bind(wx.EVT_MENU, self.OnOpen, menuItem)
        self.mnuSave = filemenu.Append(wx.ID_SAVE, "&Save Playlist")
        self.Bind(wx.EVT_MENU, self.OnSave, self.mnuSave)
        filemenu.Enable(wx.ID_SAVE, False)
        menuItem = filemenu.Append(wx.ID_SAVEAS, "Save Playlist &as...")
        self.Bind(wx.EVT_MENU, self.OnSaveAs, menuItem)
        menuItem = filemenu.Append(wx.ID_EXIT, "E&xit", " Close the program")
        self.Bind(wx.EVT_MENU, self.OnExit, menuItem)
        
        # Connection Menu
        connectmenu = wx.Menu()
        self.mnuConnect = connectmenu.Append(wx.ID_ANY, "&Connect")
        self.Bind(wx.EVT_MENU, self.OnConnectInstruction, self.mnuConnect)
        self.mnuDisconnect = connectmenu.Append(wx.ID_ANY, "&Disconnect")
        self.Bind(wx.EVT_MENU, self.OnDisconnectInstruction, self.mnuDisconnect)
        self.mnuDisconnect.Enable(False)
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
        
        # Titlebar close
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Choose a playlist", os.getcwd(), "", "*.xml", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.mp.plpath = dlg.GetPath()
            
            try:
                self.mp.playlist.loadPlaylist(self.mp.plpath)
                self.mnuSave.Enable(True)
                self.mp.plmodded = False
                
                self.mp.PlaylistRefresh()
            except Exception as e:
                wx.MessageBox('Error: {0}'.format(e.message), 'Failed to load', 
                              wx.ICON_ERROR | wx.OK)
                self.mp.plpath = ""
                self.mnuSave.Enable(False)
        dlg.Destroy()
        
    def OnSave(self, event):
        if self.mp.plpath != "":
            try:
                self.mp.playlist.savePlaylist(self.mp.plpath)
                self.mp.plmodded = False
            except Exception as e:
                wx.MessageBox('Error: {0}'.format(e.message), 'Save failed', 
                              wx.ICON_ERROR | wx.OK)                
        pass
    def OnSaveAs(self, event):
        dlg = wx.FileDialog(self, "Save playlist as", os.getcwd(), "", "*.xml", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.mp.plpath = dlg.GetPath()
            
            try:
                self.mp.playlist.savePlaylist(self.mp.plpath)
                self.mnuSave.Enable(True)
                self.mp.plmodded = False
            except Exception as e:
                wx.MessageBox('Error: {0}'.format(e.message), 'Failed to save', 
                              wx.ICON_ERROR | wx.OK)
                self.mp.plpath = ""
                self.mnuSave.Enable(False)
        dlg.Destroy()
        pass
    
    def OnExit(self, event):                    
        self.Close(True)
        
    def OnClose(self, event):
        if self.mp.plmodded == True:
            dlg = wx.MessageBox('Save Playlist?', 'Save?', wx.ICON_QUESTION | 
                                wx.YES_NO)
            if dlg == wx.YES:
                if self.mp.plpath != "":
                    self.OnSave(None)
                else:
                    self.OnSaveAs(None)
        self.Destroy()
        
    def OnConnectInstruction(self, event):
        if self.mp.server == "" or self.mp.server == ":":
            self.OnConnectOptions(None)
            if self.mp.server == "":
                wx.MessageBox('Unable to connect to invalid server', 'Error', wx.ICON_ERROR | wx.OK)
            else:
                pass
        
    def OnDisconnectInstruction(self, event):
        pass
    def OnConnectOptions(self, event):
        dlgopt = dlgConnectOptions(self)
        
        try:
            sp = self.mp.server.split(':')
            dlgopt.txtServer.Value = sp[0]
            dlgopt.txtPort.Value = sp[1]
        except IndexError:
            dlgopt.txtServer.Value = ""
            dlgopt.txtPort.Value = ""
        
        if dlgopt.ShowModal() == wx.ID_OK:
            self.mp.server = "{0}:{1}".format(dlgopt.txtServer.Value, dlgopt.txtPort.Value)
    
    def OnHelp(self, event):
        pass


class MainPanel(gui.CorePanel):
    def __init__(self, parent): 
        gui.CorePanel.__init__(self, parent)   
            
        self.playlist = Playlist()
        self.plpath = ""
        self.server = ""
        # Flag to store whether playlist is modified
        self.plmodded = False
        
        # Configure the playlist view
        self.lstPlaylist.InsertColumn(1, "Duration", width=60)
        self.lstPlaylist.InsertColumn(0, "Filename", width=self.lstPlaylist.GetSize().width - 100)
    
    def PlaylistRefresh(self):
        # Clear existing playlist items
        self.lstPlaylist.DeleteAllItems()
        
        # Add all items from list
        for filename, duration in self.playlist.playlist:
            count = self.lstPlaylist.GetItemCount()
            self.lstPlaylist.InsertStringItem(count, filename)
            self.lstPlaylist.SetStringItem(count, 1, str(duration))
        
        # Set selected item
        if self.playlist.index >= 0:
            self.lstPlaylist.Select(self.playlist.index, True)
        
        # Configure playing/loaded markers
    
    def OnMoveUp(self, event):
        if self.lstPlaylist.SelectedItemCount > 0:
            self.playlist.moveUp(self.lstPlaylist.GetFirstSelected())
            self.PlaylistRefresh()
            self.plmodded = True
            
    def OnMoveDown(self, event):
        if self.lstPlaylist.SelectedItemCount > 0:
            self.playlist.moveDown(self.lstPlaylist.GetFirstSelected())
            self.PlaylistRefresh()
            self.plmodded = True
            
    def OnRemove(self, event):
        if self.lstPlaylist.SelectedItemCount > 0:
            self.playlist.removeItem(self.lstPlaylist.GetFirstSelected())
            self.PlaylistRefresh()     
            self.plmodded = True   

    def OnPLSelect(self, event):
        if self.lstPlaylist.ItemCount > 0:
            if self.lstPlaylist.SelectedItemCount > 0:
                self.playlist.index = self.lstPlaylist.GetFirstSelected()
        else:
            self.playlist.index = -1

app = wx.App(False)
frame = MainWindow()
panel = MainPanel(frame)
frame.mp = panel
frame.Show()
app.MainLoop() 