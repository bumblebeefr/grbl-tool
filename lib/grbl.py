import serial
import os,sys,time
import re
from lib.utils import *




class Grbl:
	""" Class that wrap a serial connection to a grbl instance and allow to stream Gcode commande to GRBL CNC. """
	RX_BUFFER_SIZE = 128
	ALLOWED_START_LETTER = ("G","M","$")
	def __init__(self,device,bitrate,buffered) : 
		self.serial=None
		self.bitrate=bitrate
		self.buffered=buffered
		self.running = False

		self.l_count = 0
		self.g_count = 0
		self.c_line = []

		
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
				debug("%s seamns not to be a valid grbl connection" %dev)
				return None
		except serial.serialutil.SerialException,e:
			debug("Unable to connect to device %s : %s" %(dev,e))

	def __clean_line(self,line):
		line = line.strip()
		#add a speed ig G0 on Z axis and no speed ed
		if(re.match("G00.*Z[\-0-9\.]+.*",line.strip().upper() )and not re.match("G00.*F[\-0-9\.]+.*",line.strip().upper())):
			comment("Adding 'F100' for Z movement")
			line +=" F100"
		return line.strip()

	def streamLineBuffered(self,line):
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
				

	def stream(self,lines):
		try:
			for line in lines:
				self.streamLine(line)
		except KeyboardInterrupt :
			print
			warn("Streaming interrupted. Grbl connection will be reset to trop current processing Job")
			self.resetConnection()
			
	def seemsGcode(self,gcode):
		return len(gcode.strip()) >0 and gcode.strip()[0].upper() in Grbl.ALLOWED_START_LETTER

	def streamLine(self,line):
		self.running = True
		if(self.seemsGcode(line.strip())):
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
