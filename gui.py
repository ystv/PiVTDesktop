# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  6 2013)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class CorePanel
###########################################################################

class CorePanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 600,300 ), style = wx.TAB_TRAVERSAL )
		
		mainSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		leftSizer = wx.BoxSizer( wx.VERTICAL )
		
		leftSizer.SetMinSize( wx.Size( 100,-1 ) ) 
		self.lstPlaylist = wx.ListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_HRULES|wx.LC_NO_SORT_HEADER|wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_VRULES )
		self.lstPlaylist.SetMinSize( wx.Size( 100,-1 ) )
		
		leftSizer.Add( self.lstPlaylist, 1, wx.ALL|wx.EXPAND, 5 )
		
		plbuttonsSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btnAdd = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
		self.btnAdd.Enable( False )
		
		plbuttonsSizer.Add( self.btnAdd, 0, wx.ALL, 5 )
		
		self.btnUp = wx.Button( self, wx.ID_ANY, u"Move Up", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		plbuttonsSizer.Add( self.btnUp, 0, wx.ALL, 5 )
		
		self.btnDown = wx.Button( self, wx.ID_ANY, u"Move Down", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		plbuttonsSizer.Add( self.btnDown, 0, wx.ALL, 5 )
		
		self.btnRemove = wx.Button( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
		plbuttonsSizer.Add( self.btnRemove, 0, wx.ALL, 5 )
		
		
		leftSizer.Add( plbuttonsSizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND, 5 )
		
		
		mainSizer.Add( leftSizer, 1, wx.EXPAND, 0 )
		
		rightSizer = wx.GridBagSizer( 5, 5 )
		rightSizer.SetFlexibleDirection( wx.BOTH )
		rightSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		rightSizer.SetMinSize( wx.Size( 300,-1 ) ) 
		self.btnPlay = wx.Button( self, wx.ID_ANY, u"Play", wx.DefaultPosition, wx.Size( -1,50 ), 0 )
		self.btnPlay.Enable( False )
		
		rightSizer.Add( self.btnPlay, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.btnStop = wx.Button( self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnStop.Enable( False )
		
		rightSizer.Add( self.btnStop, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.chkAuto = wx.CheckBox( self, wx.ID_ANY, u"Auto-play next item", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		rightSizer.Add( self.chkAuto, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"00:00", wx.DefaultPosition, wx.Size( -1,80 ), wx.ALIGN_CENTRE )
		self.m_staticText1.Wrap( -1 )
		self.m_staticText1.SetFont( wx.Font( 40, 70, 90, 90, False, wx.EmptyString ) )
		self.m_staticText1.SetMaxSize( wx.Size( -1,50 ) )
		
		rightSizer.Add( self.m_staticText1, wx.GBPosition( 3, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )
		
		self.lblPlayLabel = wx.StaticText( self, wx.ID_ANY, u"Now Playing:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.lblPlayLabel.Wrap( -1 )
		rightSizer.Add( self.lblPlayLabel, wx.GBPosition( 5, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.lblPlaying = wx.StaticText( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblPlaying.Wrap( -1 )
		rightSizer.Add( self.lblPlaying, wx.GBPosition( 5, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.lblLoadLabel = wx.StaticText( self, wx.ID_ANY, u"Loaded:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.lblLoadLabel.Wrap( -1 )
		rightSizer.Add( self.lblLoadLabel, wx.GBPosition( 6, 0 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )
		
		self.lblLoaded = wx.StaticText( self, wx.ID_ANY, u"None", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.lblLoaded.Wrap( -1 )
		rightSizer.Add( self.lblLoaded, wx.GBPosition( 6, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		
		rightSizer.AddGrowableCol( 0 )
		rightSizer.AddGrowableCol( 1 )
		
		mainSizer.Add( rightSizer, 0, wx.EXPAND, 5 )
		
		
		self.SetSizer( mainSizer )
		self.Layout()
		
		# Connect Events
		self.lstPlaylist.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnPLSelect )
		self.btnAdd.Bind( wx.EVT_BUTTON, self.OnAdd )
		self.btnUp.Bind( wx.EVT_BUTTON, self.OnMoveUp )
		self.btnDown.Bind( wx.EVT_BUTTON, self.OnMoveDown )
		self.btnRemove.Bind( wx.EVT_BUTTON, self.OnRemove )
		self.btnPlay.Bind( wx.EVT_BUTTON, self.OnPlay )
		self.btnStop.Bind( wx.EVT_BUTTON, self.OnStop )
		self.chkAuto.Bind( wx.EVT_CHECKBOX, self.OnchkAutoChange )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnPLSelect( self, event ):
		event.Skip()
	
	def OnAdd( self, event ):
		event.Skip()
	
	def OnMoveUp( self, event ):
		event.Skip()
	
	def OnMoveDown( self, event ):
		event.Skip()
	
	def OnRemove( self, event ):
		event.Skip()
	
	def OnPlay( self, event ):
		event.Skip()
	
	def OnStop( self, event ):
		event.Skip()
	
	def OnchkAutoChange( self, event ):
		event.Skip()
	

