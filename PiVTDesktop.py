import wx
import os
import threading
import ctypes
import platform
import yaml
from time import sleep
from datetime import datetime
from time import mktime

import gui

from playlist import Playlist
from pivtcontrol import PiVTControl
from gui import dlgConnectOptions, dlgAddItems

CONFIGPATH = 'config.yaml'

runflag = True

class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="PiVT Desktop", size=(700,400))
        favicon = wx.Icon('PiVT_icon.ico', wx.BITMAP_TYPE_ICO)
        wx.Frame.SetIcon(self, favicon)
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
        
    def SaveConfigData(self, key, value):
        #try:
        with open(CONFIGPATH, 'r') as f:
            configdata = yaml.load(f)
            configdata[key] = value
            
        with open(CONFIGPATH, 'w') as f:
            f.write(yaml.dump(configdata))
        #except:
            #wx.MessageBox("Unable to find config file", "Warning", wx.ICON_WARNING | wx.OK)
        
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Choose a playlist", os.getcwd(), "", "*.xml", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.mp.plpath = dlg.GetPath()
            
            # Save path to config file
            self.SaveConfigData('path', os.path.dirname(self.mp.plpath))
            
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
            
            # Save path to config file
            self.SaveConfigData('path', os.path.dirname(self.mp.plpath))
            
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
                                              self.mp.DataCallback, 
                                              self.ConnFailCallback)

            self.mp.networkconn.startup_async()
        
            self.mnuDisconnect.Enable(True)
            self.mnuConnect.Enable(False)
            
        except:
            pass
        
    def ConnFailCallback(self):
        self.mp.lblConnected.SetLabel("Not Connected")
        wx.MessageBox("Connection failed", "Error", wx.ICON_ERROR | wx.OK)
        self.mnuConnect.Enable(True)
        self.mnuDisconnect.Enable(False)
        
        # Reset after disconnect
        self.OnDisconnectInstruction()
        
        
    def OnDisconnectInstruction(self, event=None):
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
        self.mp.btnAdd.Enable(False)
        
        self.mp.statusthread = None
        self.mp.clock = -1
        self.mp.clockthread = None
        
        self.mp.lblCountdown.Show(False)
        
        self.mp.StatusHighlightSet()
    
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
            
            # Save server to config file
            self.SaveConfigData('server', self.mp.server)
            
            self.OnDisconnectInstruction(None)
            self.OnConnectInstruction(None)
    
    def OnHelp(self, event):
        pass


class MainPanel(gui.CorePanel):
    def __init__(self, parent, server): 
        gui.CorePanel.__init__(self, parent)   
        
        self.playlist = Playlist()
        self.plpath = ""
        self.server = server
        self.statusthread = None
        
        # Time in milliseconds since epoch when VT finishes
        self.endtime = -1
        
        self.clockthread = None
        # Flag to store whether playlist is modified
        self.plmodded = False
        
        # Configure the playlist view
        self.lstPlaylist.InsertColumn(1, "Duration", width=60)
        self.lstPlaylist.InsertColumn(2, "Status", width=60)
        self.lstPlaylist.InsertColumn(0, "Filename", width=250)
        
        # Placeholder for networking
        self.networkconn = None
    
        
    def StatusHighlightSet(self):
        '''Run through playlist and highlight loaded and playing rows'''
        try:
            if self.networkconn.connected == True:
                playing = self.networkconn.playing
                loaded = self.networkconn.loaded
            else:
                playing = ""
                loaded = ""
                
                for i in range(0, self.lstPlaylist.GetItemCount()):
                    if self.lstPlaylist.GetItemBackgroundColour(i) != 'white':
                        self.lstPlaylist.SetItemBackgroundColour(i, 'white')
                        self.lstPlaylist.SetStringItem(i, 2, "")
        except AttributeError:
            loaded = ""
            playing = ""
            
            for i in range(0, self.lstPlaylist.GetItemCount()):
                if self.lstPlaylist.GetItemBackgroundColour(i) != 'white':
                    self.lstPlaylist.SetItemBackgroundColour(i, 'white')
                    self.lstPlaylist.SetStringItem(i, 2, "")
        
        # Clear all markers (complicated to prevent flicker from unneeded updates)
        for i in range(0, self.lstPlaylist.GetItemCount()):
            
            if self.lstPlaylist.GetItemText(i) == playing:
                self.lstPlaylist.SetItemBackgroundColour(i, 'red')
                self.lstPlaylist.SetStringItem(i, 2, "Playing")
                    
            elif self.lstPlaylist.GetItemText(i) == loaded:
                self.lstPlaylist.SetItemBackgroundColour(i, 'green')
                self.lstPlaylist.SetStringItem(i, 2, "Loaded")
                    
            elif self.lstPlaylist.GetItemBackgroundColour(i) != 'white':
                self.lstPlaylist.SetItemBackgroundColour(i, 'white')
                self.lstPlaylist.SetStringItem(i, 2, "")
    
    def PlaylistRefresh(self):
        # Clear existing playlist items
        self.lstPlaylist.DeleteAllItems()
        
        # Add all items from list
        for filename, duration in self.playlist.playlist:
            count = self.lstPlaylist.GetItemCount()
            self.lstPlaylist.InsertStringItem(count, filename)
            self.lstPlaylist.SetStringItem(count, 1, str(duration))
            self.lstPlaylist.SetStringItem(count, 2, "")
  
        # Set selected item
        if self.playlist.index >= 0:
            self.lstPlaylist.Select(self.playlist.index, True)
        
        # Configure playing/loaded markers
        self.StatusHighlightSet()
        
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
        
        dt = datetime.now()
        remtime = self.endtime - (mktime(dt.timetuple()) + dt.microsecond/1000000.0)
        
        while self.endtime != None:            
            # Update the text countdown
            m, s = divmod(remtime, 60)
            self.lblCountdown.SetLabel("{0:02d}:{1:02d}".format(int(round(m)), 
                                                           int(round(s))))

            # Set some colours on the clock
            if remtime <= 10:
                self.lblCountdown.SetForegroundColour((255,0,0))
            elif remtime <= 30:
                self.lblCountdown.SetForegroundColour((255,99,71))
            else:
                self.lblCountdown.SetForegroundColour((0, 0, 0))

            # Calculate remaining time in seconds
            dt = datetime.now()
            
            try:
                remtime = self.endtime - (mktime(dt.timetuple()) + dt.microsecond/1000000.0)
            except TypeError:
                break
            
            if (remtime <= 0):
                break

            # Sleep a while, don't hammer the CPU
            sleep(0.1)
            
        # Clean up when timer runs out
        self.lblCountdown.Show(False)
        self.lblPlaying.SetLabel("None")
        self.endtime = None
        self.clockthread = None
    
    def ConnectionCallback(self):
        self.lblConnected.SetLabel("Connected to {0}".format(self.server))
        
        self.statusthread = threading.Thread(target=self.PollStatus)
        self.statusthread.start()
        
        self.btnAdd.Enable(True)
        
        # Set the loaded item
        self.OnPLSelect(None)
        
    def DataCallback(self, seconds, changeover=False):
        """Handle updated data from server. Set changeover true to auto-advance"""
        if self.networkconn.playing != "":
            self.lblPlaying.SetLabel(self.networkconn.playing)
            self.btnStop.Enable(True)
            self.chkAuto.Enable(True)
            
            if seconds != None:
                self.endtime = calculate_end(seconds)
                if self.clockthread == None:
                    self.clockthread = threading.Thread(target=self.UpdateCountdown)
                    self.clockthread.start()
                    
            if (self.chkAuto.Value == True and changeover == True):
                self.OnPlayUpdateFromList()

        else:
            self.lblPlaying.SetLabel("None")
            self.lblCountdown.Show(False)
            self.btnStop.Enable(False)
            
            if self.endtime != None:
                self.endtime = None
                self.clockthread = None
            
        if self.networkconn.loaded != "":
            self.lblLoaded.SetLabel(self.networkconn.loaded)
            self.btnPlay.Enable(True)
            
            if (self.networkconn.playing == ""):
                m, s = divmod(seconds, 60)
                self.lblCountdown.SetLabel("{0:02d}:{1:02d}".format(int(round(m)), 
                                                                    int(round(s))))
                self.lblCountdown.SetForegroundColour((0, 0, 0))
                self.lblCountdown.Show(True)
            
        else:
            self.lblLoaded.SetLabel("None")
            self.btnPlay.Enable(False)
            
        # Fix red/green highlights
        self.StatusHighlightSet()
        
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
                            self.btnPlay.Enable(False)
                        self.chkAuto.SetLabel("Auto-play selected item")
                    else:
                        self.GetParent().OnDisconnectInstruction()
                        raise AttributeError
                except AttributeError:
                    pass
            else:
                if self.chkAuto.Value == False:
                    self.playlist.index = -1
        else:
            self.playlist.index = -1
            
    def OnPlayUpdateFromList(self):
        if self.playlist.index >= len(self.playlist.playlist):
            self.playlist.index = -1
            self.OnStop(None)
            return
        
        plitem, plduration = self.playlist.playlist[self.playlist.index]
        
        if self.networkconn.playing != plitem:
            for item, duration in self.playlist.playlist:
                if item == self.networkconn.playing:
                    plitem = item
                    plduration = duration
                    
        if self.networkconn.playing == plitem:                
            # Deselect current item
            self.lstPlaylist.Select(self.lstPlaylist.GetFirstSelected(), False)
            
            # Change the checkbox label to play selected
            self.chkAuto.SetLabel('Auto-play next item')
                
            # Update the status markers
            self.StatusHighlightSet()
            
            # Load next if needed
            if (self.chkAuto.Value == True and self.networkconn.loaded == ""):
                item, duration = self.playlist.getNextItem(advance=True)
                self.networkconn.load(item)
                self.lblLoaded.SetLabel('Please Wait...')
                self.btnPlay.Enable(False)
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
        
        # Update playing statuses from playlist
        self.OnPlayUpdateFromList()

                
    def OnStop(self, event):
        self.networkconn.stop()
        self.btnStop.Enable(False)
        self.lblPlaying.SetLabel("None")
        self.lblCountdown.Show(False)
        self.endtime = None
        self.chkAuto.SetLabel('Auto-play next item')
        self.chkAuto.Value = False
        self.chkAuto.Enable(False)
        self.networkconn.setauto(False)
        self.StatusHighlightSet()
        
    def OnchkAutoChange(self, event):
        try:
            if self.networkconn.connected == True:
                self.networkconn.setauto(self.chkAuto.Value)
                
                if (self.chkAuto.Value == True):
                    # Set current selection in playlist if not set already
                    if (self.playlist.index == -1):
                        if (self.networkconn.playing != ""):
                            for i in range(0, len(self.playlist.playlist)):
                                item, duration = self.playlist.playlist[i]
                                if item == self.networkconn.playing:
                                    self.playlist.index = i
                                    break

                    if (self.networkconn.loaded == ""):
                        # Load the next playlist item if requested
                        item, duration = self.playlist.getNextItem(advance=True)
                        self.networkconn.load(item)
                        self.lblLoaded.SetLabel('Please Wait...')
                        self.btnPlay.Enable(False)
            else:
                self.GetParent().OnDisconnectInstruction()
                raise AttributeError
        except AttributeError:
            self.chkAuto.Enable(False)
            self.chkAuto.Value = False
            
            
    def OnAdd(self, event):
        dlgAdd = dlgAddItems(self)
        filelist = self.networkconn.getfilelist()
        for item, duration in filelist:
            dlgAdd.ddVideoList.Append(item)
        
        if dlgAdd.ShowModal() == wx.ID_OK:
            if self.lstPlaylist.SelectedItemCount > 0:
                newindex = self.playlist.index
            else:
                newindex = -1
                
            for item, duration in filelist:
                if item == dlgAdd.ddVideoList.GetStringSelection():
                    self.playlist.addItem(item, int(round(duration)), )
                    self.PlaylistRefresh()

def calculate_end(time):
    """Calculate the end time in seconds since epoch based on a time from now """
    dt = datetime.now()
    currenttime = mktime(dt.timetuple()) + dt.microsecond/1000000.0
    return currenttime + time

# Reconfigure so the icon is correct on Windows
if platform.system() == 'Windows':
    myappid = 'YSTV.PiVT.PiVTDesktop.2.0' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
       
       
# Try and read a config file
server = ''
defaultpath = os.getcwd()
try:
    with open(CONFIGPATH, 'r') as f:
        configdata = yaml.load(f)
        server = configdata['server']
        defaultpath = configdata['path']
        if defaultpath == '':
            defaultpath = os.getcwd()
except IOError:
    print "Where's my config file gone??"

# Small hack so working directory changes don't break config file
CONFIGPATH = os.path.join(os.getcwd(), CONFIGPATH)
    
# App setup and run
app = wx.App(False)
frame = MainWindow()
panel = MainPanel(frame, server)
frame.mp = panel
os.chdir(defaultpath)
frame.Show()
app.MainLoop() 