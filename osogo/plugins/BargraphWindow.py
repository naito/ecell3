#!/usr/bin/env python

import  gtk 
from Numeric import *
import gtk.gdk
import re
import string
import operator
from PlotterPluginWindow import *
from Plot import *
from ecell.ecssupport import *
BAR_WIDTH=150
BAR_HEIGTH=20
class BargraphWindow( OsogoPluginWindow ):

	def __init__( self, dirname, data, pluginmanager, root=None ):
		#initializa variables:
		#initiates window
		OsogoPluginWindow.__init__(self, dirname, data, pluginmanager,\
		    				root)

		self.openWindow()
		#this should be removed:
		root=self.getWidget('BargraphWindow')
		#gets HandleBox
		self.handlebox=self.getWidget('handlebox1')
		self.drawingarea=self.getWidget('drawingarea1')
		self.numberlabel=self.getWidget('label4')
		self.textlabel=self.getWidget('label5')
		self.arrow=self.getWidget('image1')
		self.button=self.getWidget('togglebutton1')
		self.buttonstate=1
		self.button.set_active(self.buttonstate)
		#sets callback for drawingarea
		#sets up picturebuffer
		self.ColorMap=self.handlebox.get_colormap()
		
		#sets colorcodes, codetable
		#codetable: list, range upper boundaries in ascendingorder, GDKColor codes
		self.colored_ranges=[
			    [-1,'black',None], #overload
			    [0,'grey',None], #default background
			    [10,'blue',None],
			    [100,'yellow',None],
			    [1000,'red',None]]
			    
		for i in range(len(self.colored_ranges)):
		    gc=root.window.new_gc()
		    gc.set_foreground(\
			self.ColorMap.alloc_color(self.colored_ranges[i][1]))
		    self.colored_ranges[i][2]=gc
		self.theSession=pluginmanager.theSession
		#lastvalue zero
		self.lastvalue=0
		self.lastscale=0
		self.lastposition=0
		#paint pixbuf according to lastvalue - draw everything to default
		self.pm=gtk.gdk.Pixmap(root.window,BAR_WIDTH,BAR_HEIGTH,-1)
		
		self.pm.draw_rectangle(self.colored_ranges[1][2],gtk.TRUE,0,0,
			    BAR_WIDTH,BAR_HEIGTH)

		self.addHandlers({\
		    'drawingarea1_expose_event':self.expose,
		    'togglebutton1_toggled':self.press})

		self.drawingarea.queue_draw_area(0,0,BAR_WIDTH, BAR_HEIGTH)			
		#calls update
		pluginmanager.appendInstance(self)
		self.ccFullPN=convertFullIDToFullPN(self.theFullID(),
		'Value')
		nameFullPN=str(self.ccFullPN[SYSTEMPATH])+':'+\
		    str(self.ccFullPN[ID])
		self.textlabel.set_text(nameFullPN)

		self.update()

	def update(self):
	    #getlatest data
	    #currentvalue=self.theFullPN
	    self.current_value=self.getlatestdata()
	    self.numberlabel.set_text(str(self.current_value))
	    #calculate scale
	    self.current_scale=self.get_scale(self.current_value)
	    if self.current_scale==0:
	    #paint the whole area black, lastvalue, lastposition, lastscale=0
		self.pm.draw_rectangle(self.colored_ranges[0][2],gtk.TRUE,0,0,
			    BAR_WIDTH,BAR_HEIGTH)
		self.drawingarea.queue_draw_area(0,0,BAR_WIDTH,BAR_HEIGTH)
		self.lastvalue=0
		self.lastposition=0
		self.lastscale=0
	    else:
		#calculate direction
		difference=self.current_value-self.lastvalue
		if difference>0:
		    icon_id=gtk.STOCK_GO_UP
		elif difference<0:
		    icon_id=gtk.STOCK_GO_DOWN
		else:
		    icon_id=gtk.STOCK_REMOVE
		self.arrow.set_from_stock(icon_id,4)  
		self.current_position=self.convert_value(self.current_value)
		#if scalechange, drawall
		if self.lastscale!=self.current_scale:
		    #draw painted area and draw grey area
		    self.pm.draw_rectangle(self.colored_ranges[self.current_scale][2],
			gtk.TRUE,0,0,self.current_position,BAR_HEIGTH)
		    self.pm.draw_rectangle(self.colored_ranges[1][2],gtk.TRUE,
			self.current_position,0,BAR_WIDTH-self.current_position,
			BAR_HEIGTH)
		    self.drawingarea.queue_draw_area(0,0,BAR_WIDTH,BAR_HEIGTH)
		else:	
		#if not scalechange 
		    if difference<0:
			brush=self.colored_ranges[1][2]
			x0=self.current_position
			width=self.lastposition-self.current_position
		    #if difference is negativ, paint with grey,
		    elif difference>0:
			brush=self.colored_ranges[self.current_scale][2]
			x0=self.lastposition
			width=self.current_position-self.lastposition
		    #if difference ispositiv , paint with proper color
		    else:
			return True #do not draw if no changes
		    self.pm.draw_rectangle(brush,gtk.TRUE,x0,0,width,BAR_HEIGTH)
		    self.drawingarea.queue_draw_area(x0,0,width,BAR_HEIGTH) 
		self.lastvalue=self.current_value
		self.lastscale=self.current_scale
		self.lastposition=self.current_position
	    return True
	
	def convert_value(self,aValue):
	    if self.current_scale>1:
		return round((aValue-self.colored_ranges[self.current_scale-1][0])/\
		    self.colored_ranges[self.current_scale][0]*BAR_WIDTH)
	    else:
		return 0
		
	def expose(self, obj, event):
	    obj.window.draw_drawable(self.pm.new_gc(),self.pm,event.area[0],event.area[1],
				    event.area[0],event.area[1],event.area[2],event.area[3])
	
	def press(self, obj):
	    self.button.set_active(self.buttonstate)

	def getlatestdata(self):
#	    newFullPN[3]='Concentration'
#	    print newFullPN
	    return self.getValue(self.ccFullPN)
	    
	def get_scale(self,value): 
	    no_scales=len(self.colored_ranges)
	    if value<self.colored_ranges[1][0] or\
		value>self.colored_ranges[no_scales-1][0]:
		#the whole bar should be painted black
		return 0
	    else:
		for i in range(2,no_scales):
		    if self.colored_ranges[i][0]>=value:
			return i
