from utils import *
from math import *
import macros
import os,sys,time
import pygame
import joystick

class Macro:
	_joystick=None
	_joystick_inc = 1

	
	def __init__(self,grbl):
		self.grbl = grbl
		
	def abs(self):
		"""Switch to absolute positioning (G90)"""
		comment("Switching to absolute positioning")
		self.grbl.streamLine("G90")

	def rel(self):
		"""Switch to relative/incremental positioning (G91)"""
		comment("Switching to relative/incremental positioning")
		self.grbl.streamLine("G91")

	def zero(self):
		"""Switch to absolute positioning, and reseting origin to current position."""
		comment("Switching to absolute positioning, and reseting origin to current position")
		self.grbl.stream(("G91","G92 X0 Y0 Z0"))

	def stream(self,filename):
		"""Stream the specified file to grbl. You can specify absolute path of the file, or name of a file in the gcode folder."""
		pathname = os.path.dirname(sys.argv[0]) # current script's path
		if(not filename.startswith("/")):
			filename = os.path.abspath("%s/gcode/%s" % (pathname,filename))
		if(os.path.isfile(filename)):
			comment("Start streaming %s file" %filename)
			f = open(filename, 'r')
			self.grbl.stream(f)
			f.close()
		else:
			warn("No such file %s" %filename)
			
	def ls(self):
		"""List files to stream ind the gcode filder."""
		pathname = os.path.dirname(sys.argv[0]) # current script's path
		for f in os.listdir("%s/gcode/" % pathname) :
			print(f)

			
	def help(self):
		"""Show this help"""
		print"""
You can manually send commands to grbl that can be : 
 - A regular GCODE command such as : 
		G0/G00 	Switch to rapid linear motion mode (seek)
		G1/G01 	Switch to linear motion at the current feed rate 	Used to cut a straight line
		G2/G02 	Switch to clockwise arc mode 
		G3/G03 	Switch to anti-clockwise arc mode 
		G4/G04 	Dwell (pause) 
		G17 	Select the XY plane (for arcs) 
		G18 	Select the XZ plane (for arcs) 
		G19 	Select the YZ plane (for arcs) 
		G20 	After this, units will be in inches 
		G21 	After this, units will be in mm
		G28 	Return to home position 	(to-do: compare with G30)
		G30 	Return to home position 	(to-do: compare with G28)
		G90 	Switch to absolute distance mode 
		G91 	Switch to incremental distance mode 
		G92 	Change the current coordinates without moving 
		G93 	Set inverse time feed rate mode
		G94 	Set units per minute feed rate mode 
 - '$' :  show current grbl settings
 - '$x=value' : set a parameter
 - 'exit' : exit this tool"""
		for m in dir(self):
			if( not m.startswith("_")):
				print(" - %s : %s"%(m,getattr(self,m).__doc__))




	def joystick(self):
		info("Starting joystickMode")
		if(self._joystick == None):
			self._joystick = joystick.Joystick()
		self.grbl.streamLine("G91")
		try :
			while(True):
				axes = self._joystick.getAxisValues()
				if(not(axes[0]==0 and axes[1]==0 and axes[2]==0)):
					move = [x*self._joystick_inc for x in axes]
					move[3] = round(max(fabs(axes[0]),fabs(axes[1]),fabs(axes[2]))*160)
					t=sqrt(axes[0]**2+axes[1]**2+axes[2]**2) / move[3]*60
					gcd = "G01 X%s Y%s Z%s F%s" % tuple(move)
					self.grbl.streamLine(gcd)
					debug("sleep %ss"%t)
					time.sleep(t)
				else :
					time.sleep(0.001)
		except joystick.NoJoystickException, e:
			warn (e)
		except KeyboardInterrupt, e:
			info("Exiting joystick mode")

