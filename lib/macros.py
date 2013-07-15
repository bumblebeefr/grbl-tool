from utils import *
from math import *
import os, sys, time


class Macro:
    def __init__(self, grbl):
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
        self.grbl.stream(("G90", "G92 X0 Y0 Z0"))

    def stream(self, filename, *args):
        """Stream the specified file to grbl. You can specify absolute path of the file, or name of a file in the gcode folder. You can add somme addition argument fter file name:
     - 'debug':  stream the file step by step
     - 'limit':  try add a Z feed rate limitation
     - 'buffered': use buffered mode to stream the file"""
        pathname = os.path.dirname(sys.argv[0])  # current script's path
        if("buffered" in args):
            self.grbl.buffered = True
        if("limit" in args):
            self.grbl.zLimit = True
        if(not filename.startswith("/")):
            filename = os.path.abspath("%s/gcode/%s" % (pathname, filename))
        if(os.path.isfile(filename)):
            comment("Start streaming %s file" % filename)
            f = open(filename, 'r')
            try:
                self.grbl.stream(f, "debug" in args)
            except KeyboardInterrupt:
                print
                warn("Streaming interrupted. Grbl connection will be reset to stop current processing Job")
                self.grbl.resetConnection()
            f.close()
        else:
            warn("No such file %s" % filename)
        self.grbl.buffered = False
        self.grbl.zLimit = False

    def ls(self):
        """List .ngc files to stream from the gcode filder."""
        pathname = os.path.dirname(sys.argv[0])  # current script's path
        for f in os.listdir("%s/gcode/" % pathname):
            if(f.upper().endswith(".NGC")):
                print(f)

    def clear(self):
        os.system("clear")

    def help(self, cmd=None):
        """Show this help"""
        if(cmd in dir(self)):
            print(getattr(self, cmd).__doc__)
        else:
            print"""
You can manually send commands to grbl that can be:
 - A regular GCODE command such as:
        G0/G00     Switch to rapid linear motion mode (seek)
        G1/G01     Switch to linear motion at the current feed rate     Used to cut a straight line
        G2/G02     Switch to clockwise arc mode
        G3/G03     Switch to anti-clockwise arc mode
        G4/G04     Dwell (pause)
        G17     Select the XY plane (for arcs)
        G18     Select the XZ plane (for arcs)
        G19     Select the YZ plane (for arcs)
        G20     After this, units will be in inches
        G21     After this, units will be in mm
        G28     Return to home position     (to-do: compare with G30)
        G30     Return to home position     (to-do: compare with G28)
        G90     Switch to absolute distance mode
        G91     Switch to incremental distance mode
        G92     Change the current coordinates without moving
        G93     Set inverse time feed rate mode
        G94     Set units per minute feed rate mode
 - '$':  show current grbl HELP
 - 'exit': exit this tool"""
            for m in dir(self):
                if(not m.startswith("_")):
                    print(" - %s: %s" % (m, getattr(self, m).__doc__))
