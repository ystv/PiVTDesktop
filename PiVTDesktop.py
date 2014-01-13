import wx
import os
import threading

import gui

from playlist import Playlist
from pivtcontrol import PiVTControl
from gui import dlgConnectOptions
from time import sleep

DEFAULTSERVER = 'sn-pi:9815'

runflag = True

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
        if self.mp.networkconn != None:
            self.mp.networkconn.run = False
            
        if self.mp.plmodded == True:
            dlg = wx.MessageBox('Save Playlist?', 'Save?', wx.ICON_QUESTION | 
                                wx.YES_NO)
            if dlg == wx.YES:
                if self.mp.plpath != "":
                    self.OnSave(None)
                else:
                    self.OnSaveAs(None)
        
        if self.mp.statusthread != None:
            self.mp.statusthread.join()
        
        self.Destroy()
        
    def OnConnectInstruction(self, event):
        if self.mp.server == "" or self.mp.server == ":":
            self.OnConnectOptions(None)
            if self.mp.server == "":
                wx.MessageBox('Unable to connect to invalid server', 'Error', wx.ICON_ERROR | wx.OK)
                return
            else:
                pass
            
        if self.mp.networkconn != None:
            self.mp.networkconn.run = False
            
        self.mp.lblConnected.SetLabel("Connecting to {0}".format(self.mp.server))
        
        try: 
            self.mp.networkconn = PiVTControl(self.mp.server, 
                                              self.mp.ConnectionCallback, 
                                              self.mp.DataCallback)

            self.mp.networkconn.startup_async()
        
            self.mnuDisconnect.Enable(True)
            self.mnuConnect.Enable(False)
            
        except:
            pass
        
    def OnDisconnectInstruction(self, event):
        if self.mp.networkconn != None:
            self.mp.networkconn.run = False
            self.mp.networkconn = None
            
        # Lots of UI reset to do
        self.mnuConnect.Enable(True)
        self.mnuDisconnect.Enable(False)
        self.mp.lblConnected.SetLabel("Not Connected")
        
        self.mp.lblPlaying.SetLabel("None")
        self.mp.lblLoaded.SetLabel("None")
        self.mp.btnPlay.Enable(False)
        self.mp.btnStop.Enable(False)
        
        self.mp.statusthread = None
        self.mp.clock = -1
        self.mp.clockthread = None
    
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
            
            self.OnDisconnectInstruction(None)
            self.OnConnectInstruction(None)
    
    def OnHelp(self, event):
        pass


class MainPanel(gui.CorePanel):
    def __init__(self, parent): 
        gui.CorePanel.__init__(self, parent)   
            
        self.playlist = Playlist()
        self.plpath = ""
        self.server = DEFAULTSERVER
        self.statusthread = None
        self.clock = -1
        self.clockthread = None
        # Flag to store whether playlist is modified
        self.plmodded = False
        
        # Configure the playlist view
        self.lstPlaylist.InsertColumn(1, "Duration", width=60)
        self.lstPlaylist.InsertColumn(0, "Filename", width=self.lstPlaylist.GetSize().width - 100)
        
        # Placeholder for networking
        self.networkconn = None
    
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
        
    def PollStatus(self):
        time = 9.9
        while self.networkconn != None and self.networkconn.run == True:
            if time >= 10:
                self.networkconn.get_info()
                time = 0
            else:
                sleep(0.5)
                time = time + 0.5
                
    def UpdateCountdown(self):
        self.lblCountdown.Show(True)
        while self.clock > 0:
            # Update the text countdown
            m, s = divmod(self.clock, 60)
            self.lblCountdown.SetLabel("{0:02d}:{1:02d}".format(int(round(m)), 
                                                           int(round(s))))

            # Set some colours on the clock
            if self.clock <= 10:
                self.lblCountdown.SetForegroundColour((255,0,0))
            elif self.clock <= 30:
                self.lblCountdown.SetForegroundColour((255,99,71))
            else:
                self.lblCountdown.SetForegroundColour((0, 0, 0))

            # This aims to count whole seconds until video end
            x = self.clock % 1
            if x < 0.2:
                x = x + 1
                
            self.clock = self.clock - x
            sleep(x)
            
        # Clean up when timer runs out
        self.lblCountdown.Show(False)
        self.lblPlaying.SetLabel("None")
        self.clock = None
        self.clockthread = None
        
        # Handle an auto play if set
        if self.chkAuto.Value == True:
            self.networkconn.playing = self.networkconn.loaded
            self.OnPlayUpdateFromList()
    
    def ConnectionCallback(self):
        self.lblConnected.SetLabel("Connected to {0}".format(self.server))
        
        self.statusthread = threading.Thread(target=self.PollStatus)
        self.statusthread.start()
        
        # Set the loaded item
        self.OnPLSelect(None)
        
    def DataCallback(self, seconds):
        if self.networkconn.playing != "":
            self.lblPlaying.SetLabel(self.networkconn.playing)
            self.btnStop.Enable(True)
            self.chkAuto.Enable(True)
            
            if seconds != None:
                self.clock = seconds
                if self.clockthread == None:
                    self.clockthread = threading.Thread(target=self.UpdateCountdown)
                    self.clockthread.start()
                
        else:
            self.lblPlaying.SetLabel("None")
            self.lblCountdown.Show(False)
            self.btnStop.Enable(False)
            
            if self.clock != -1:
                self.clock = -1
                self.clockthread = None
            
        if self.networkconn.loaded != "":
            self.lblLoaded.SetLabel(self.networkconn.loaded)
            self.btnPlay.Enable(True)
        else:
            self.lblLoaded.SetLabel("None")
            self.btnPlay.Enable(False)

        self.chkAuto.Value = self.networkconn.automode
        
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
                
                # Load a new item if we're connected
                try:
                    if self.networkconn.connected == True:
                        if self.networkconn.loaded != self.playlist.getCurrentItemName():
                            self.networkconn.load(self.playlist.getCurrentItemName())
                            self.lblLoaded.SetLabel("Please Wait...")
                        self.chkAuto.SetLabel("Auto-play selected item")
                except AttributeError:
                    pass

        else:
            self.playlist.index = -1
            
    def OnPlayUpdateFromList(self):
        plitem, plduration = self.playlist.playlist[self.playlist.index]
        
        if self.networkconn.playing != plitem:
            for item, duration in self.playlist.playlist:
                if item == self.networkconn.playing:
                    plitem = item
                    plduration = duration
                    
        if self.networkconn.playing == plitem:
            # Fix the clock
            self.clock = float(plduration)
            if self.clockthread == None:
                self.clockthread = threading.Thread(target=self.UpdateCountdown)
                self.clockthread.start()
                
            # Deselect current item
            self.lstPlaylist.Select(self.lstPlaylist.GetFirstSelected(), False)
            
            # Change the checkbox label to play selected
            self.chkAuto.SetLabel('Auto-play next item')
            
            # Load the next playlist item if requested
            if self.chkAuto.Value == True:
                item, duration = self.playlist.getNextItem()
                self.networkconn.load(item)
                self.lblLoaded.SetLabel('Please Wait...')
        else:
            self.lblLoaded.SetLabel("None")
            self.btnPlay.Enable(False)
                
            
    def OnPlay(self, event):        
        # Play the loaded item
        self.networkconn.play()
        
        # Update the labels
        self.lblPlaying.SetLabel(self.networkconn.playing)
        self.btnStop.Enable(True)
        self.chkAuto.Enable(True)
        
        # Set the red blob
        
        # Update playing statuses from playlist
        self.OnPlayUpdateFromList()

                
    def OnStop(self, event):
        self.networkconn.stop()
        self.btnStop.Enable(False)
        self.lblPlaying.SetLabel("None")
        self.lblCountdown.Show(False)
        self.clock = -1
        self.chkAuto.SetLabel('Auto-play next item')
        self.chkAuto.Value = False
        self.chkAuto.Enable(False)
        self.networkconn.setauto(False)
        
    def OnchkAutoChange(self, event):
        try:
            if self.networkconn.connected == True:
                self.networkconn.setauto(self.chkAuto.Value)
                if (self.networkconn.loaded == ""):
                    # Load the next playlist item if requested
                    item, duration = self.playlist.getNextItem()
                    self.networkconn.load(item)
                    self.lblLoaded.SetLabel('Please Wait...')
            else:
                raise AttributeError
        except AttributeError:
            self.chkAuto.Enable(False)
            self.chkAuto.Value = False
            
        
app = wx.App(False)
frame = MainWindow()
panel = MainPanel(frame)
frame.mp = panel
frame.Show()
app.MainLoop() 