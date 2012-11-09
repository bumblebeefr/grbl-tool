
class Color:
	RESET='\033[39m\033[0m'
	DEFAULT='\033[39m'
	BLACK='\033[30m'
	RED='\033[31m'
	GREEN='\033[32m'
	YELLOW='\033[33m'
	BLUE='\033[34m'
	MAGENTA='\033[35m'
	CYAN='\033[36m'
	WHITE='\033[37m'
	STRONG='\033[1m'
	LIGHT='\033[0m'
	UNDERLINE='\033[4m'

def info(s):
	#if (not args.quiet):
		print("%s=== %s%s" % (Color.STRONG,s,Color.RESET))
	
def log_in(s):
	#if (not args.quiet):
		print("%s<<< %s%s" % (Color.CYAN,s,Color.RESET))
	
def log_out(s):
	#if (not args.quiet):
		print("%s>>> %s%s" % (Color.GREEN,s,Color.RESET))
	
def comment(s):
	#if (not args.quiet):
		print("%s### %s%s" % (Color.STRONG+Color.BLACK,s,Color.RESET))
	
def debug(s):
	#if(args.verbose and not args.quiet):
		print("%s!!! %s%s" % (Color.MAGENTA,s,Color.RESET))
	
def warn(s):
	#if (not args.quiet):
		print("%s/!\ %s%s" % (Color.YELLOW,s,Color.RESET))
