#!/usr/bin/env python
"""\
Stream g-code to grbl controller

This script differs from the simple_stream.py script by 
tracking the number of characters in grbl's serial read
buffer. This allows grbl to fetch the next line directly
from the serial buffer and does not have to wait for a 
response from the computer. This effectively adds another
buffer layer to prevent buffer starvation.

TODO: - Add runtime command capabilities

Version: SKJ.20120110
"""


import argparse
import readline
from lib.utils import *
from lib.grbl import *
import lib.macros


cmd_startup = """
=================== Command line mode ===================

You can manually send commands to grbl that can be : 
 - '$' to show current grbl settings
 - '$x=value' to set a parameter
 - 'exit' to exit this tool
 - 'help' to show more help   
 
=========================================================
"""


def processCommand(grbl,macro,strCmd):
	strCmd = strCmd.strip()
	cmdSplit = strCmd.split(" ")
	if strCmd.upper() == "EXIT":
		return False
	elif(hasattr(macro,cmdSplit[0])):
		debug("Command found")
		args = cmdSplit[1:]
		try:
			getattr(macro,cmdSplit[0])(*args)
		except TypeError,e:
			warn("Error  :%s" % e)
	elif (not grbl.isComment(strCmd)):
		grbl.streamLine(strCmd)
	return True

def main():
	global args
	pathname = os.path.dirname(sys.argv[0]) # current script's path
	parser = argparse.ArgumentParser(description='Tool to stream GCODE to a GRBL driver machine.')
	parser.add_argument('-v','--verbose', action="store_true",help='Verbose output, Show more informations' )
	parser.add_argument('-q','--quiet', action="store_true", help='Force no output,even if verbose mode is active' )
	parser.add_argument('-b','--buffered', action="store_true", help='Force no output,even if verbose mode is active' )
	parser.add_argument('-d','--device', nargs='?',default=None, help='Serila device to be used. If none defined, it will try to find it automaticaly.' )
	parser.add_argument('--bitrate', nargs='?',default=9600, help='Serila device to be used. If none defined, it will try to find it automaticaly.' )
	parser.add_argument('-s','--stream', nargs='?', type=argparse.FileType('r'),default=None, help='Input file to be parsed, if not specified tool will be launch as a manual command line interface')
	try :
		args = parser.parse_args()
	except IOError :
		sys.exit(0)
		
	if(os.path.isfile(os.path.join(pathname,".history"))):
		readline.read_history_file(os.path.join(pathname,".history"))
	
	# Initialize
	grbl = Grbl(args.device,args.bitrate,args.buffered)
	macro = lib.macros.Macro(grbl)
	try : 
		if(args.stream == None):
			print Color.STRONG+cmd_startup+Color.RESET
			grbl.buffered = False
			while True:
				line=raw_input(" ~ ")
				if (not processCommand(grbl,macro,line)):
					info("Exiting ...")
					break;
		else:
			comment("Start Streaming")
			grbl.stream(args.stream)
	except KeyboardInterrupt :
		print
		info("Exiting ...")

	# Wait for user input after streaming is completed
	if(grbl.running):
		warn("WARNING: Wait until grbl completes buffered g-code blocks before exiting.")
		try:
			raw_input("    Press <Enter> to exit and disable grbl.") 
		except KeyboardInterrupt :
			print
	
	# Close file and serial port
	if(args.stream != None) :
		args.stream.close()
	grbl.close()
	readline.set_history_length(1500)
	readline.write_history_file(os.path.join(pathname,".history"))




if __name__ == "__main__":
	sys.exit(main())
