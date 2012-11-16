import serial
import os,sys,time,math
import re
from lib.utils import *




class Grbl:
	""" Class that wrap a serial connection to a grbl instance and allow to stream Gcode commande to GRBL CNC. """
	RX_BUFFER_SIZE = 128
	def __init__(self,device,bitrate,buffered) : 
		self.serial=None
		self.bitrate=bitrate
		self.buffered=buffered
		self.running = False

		self.l_count = 0
		self.g_count = 0
		self.c_line = []

		self.defaultSpeed=500
		self.zSpeed=150
		self.zLimit = False

		self.lastPosition = [0,0,0,0]

		
		if(device != None):# try to find an arduino tty connection (only *nux os supported) //TODO try initate grbl com in case of multiple usbtty
			self.serial = self.__initializeSerialPort(device)
		if(self.serial == None):
			for f in os.listdir("/dev/"):
				if(f.find("ttyUSB") ==0 or f.find("ttyACM") == 0 ):
					dev="/dev/"+f
					self.serial=self.__initializeSerialPort(dev)
					if (self.serial != None):
						break;
		if(self.serial == None):
			warn("Unable to connect to a Grbl device")
			exit(1)
		

	def __initializeSerialPort(self,dev):
		"""Try to initalise a Serial connection to the specified device. Return the  device if we are connected to a vlaid Grbl device, None otherwise. """
		debug("Initializing grbl connection to %s ..." %dev)
		try :
			s = serial.Serial(dev,self.bitrate)
			# Wake up grbl
			s.write("\r\n\r\n")
			initialized=None
			s.timeout=0
			time.sleep(2)
			for i in range(4):
				val = s.readline()
				if("GRBL" in val.upper()):
					initialized = val
					break
			if(initialized != None):
				info("Connected on %s : %s" % (dev,initialized))
				s.timeout=None
				s.flushInput()
				self.device = dev
				return s
			else :
				debug("%s seams not to be a valid grbl connection" %dev)
				return None
		except serial.serialutil.SerialException,e:
			debug("Unable to connect to device %s : %s" %(dev,e))

	def __clean_line(self,line):
		line = line.strip().upper()
		#add a speed ig G0 on Z axis and no speed ed
		#if(re.match("G00.*Z[\-0-9\.]+.*",line.strip().upper() )and not re.match("G00.*F[\-0-9\.]+.*",line.strip().upper())):
		#	comment("Adding 'F100' for Z movement")
		#	line +=" F100"
		if(self.zLimit) :
			if(line.startswith("G1 ") or line.startswith("G0 ") or line.startswith("G01") or line.startswith("G00") or line.startswith("X") or line.startswith("Y") or line.startswith("Z")):
				line = self._limitZSpeed(line)
		return line.strip()
		
	def _getValue(self,line,k):
		a = re.findall(k+"[\\-0-9\\.]*",line)
		if(len(a) >0):
			return float(a[0][1:])
		else:
			return 0

	def _limitZSpeed(self,line):
		position = [self._getValue(line,"X"),self._getValue(line,"Y"),self._getValue(line,"Z"),self._getValue(line,"F")]
		x=position[0]-self.lastPosition[0]
		y=position[1]-self.lastPosition[1]
		z=position[2]-self.lastPosition[2]
		f=position[3]
		#debug("Translation %s %s %s %s"%(x,y,z,f))
		if(f == 0):
			f= self.defaultSpeed
		if(z != 0):
			v = self.zSpeed * math.sqrt(x**2+y**2+z**2)/abs(z)
			#debug("Compurted speed %s" %v)
			if (v < f ) :
				comment("Z speed limit detected, auto reducing feed rate")
				line = re.sub("F[0-9\\.]*","",line) #Suppress 'F' elements
				line = "%s F%.4f" % (line,v) #Add corrected Feed Rate
		position[3] = f
		self.lastPosition = position
		
		return line

	def streamLineBuffered(self,line): #TODO Est ce vraiment utile de maitenir ce buffered mode ?
		"""Send/Stream the specified GCODE Command line to grbl by using buffered streamin"""
		self.l_count += 1 # Iterate line counter
		l_block = self.__clean_line(line)
		self.c_line.append(len(l_block)+1) # Track number of characters in grbl serial read buffer
		grbl_out = '' 
		while sum(self.c_line) >= Grbl.RX_BUFFER_SIZE-1 | self.serial.inWaiting() :
			out_temp = self.serial.readline().strip() # Wait for grbl response
			if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
				log_in(out_temp) # Debug response
			else :
				if(out_temp.find('error') != -1) :
					warn("Grbl "+out_temp);
				grbl_out += out_temp;
				self.g_count += 1 # Iterate g-code counter
				grbl_out += str(self.g_count); # Add line finished indicator
				del self.c_line[0]
		debug("Line:"+str(self.l_count))
		log_out(l_block)
		self.serial.write(l_block + '\n') # Send block to grbl
		debug("BUF:"+str(sum(self.c_line))+" REC:"+grbl_out)


	def streamLineUnbuffered(self,line) : 
		l_block = self.__clean_line(line)
		log_out(l_block)
		self.serial.write(l_block + '\n') # Send block to grbl
		while True :
			out_temp = self.serial.readline().strip()
			if (out_temp.find('ok') !=-1 ) :
				log_in(out_temp)
				break
			elif (out_temp.find('error') !=-1 ) :
				warn(out_temp)
				break
			else :
				log_in(out_temp)
				

	def stream(self,lines,debug=False,delay = 0):
		try:
			for line in lines:
				self.streamLine(line)
				time.sleep(0.01)
				if debug :
					raw_input("")
		except KeyboardInterrupt :
			print
			warn("Streaming interrupted. Grbl connection will be reset to trop current processing Job")
			self.resetConnection()
			
	def isComment(self,gcode):
		gcode = gcode.strip()
		return gcode.startswith("%") or len(gcode) ==0 or (gcode.startswith("(") and gcode.endswith(")"))




	def streamLine(self,line):
		self.running = True
		if(not self.isComment(line.strip())):
			if(self.buffered) :
				self.streamLineBuffered(line)
			else :
				self.streamLineUnbuffered(line)
		elif(len(line.strip()) >0 ):
			comment(line.strip())


	def close(self):
		self.serial.close()

	def resetConnection(self):
		self.serial.close()
		self.running = False
		self.serial.open()
		time.sleep(2)
		self.serial.flushInput()
