from math import *
from utils import *
import os
import sys


class Macro:
    def __init__(self, grbl):
        self._grbl = grbl
        self._alias = {
            "?": "status"
        }

    def abs(self):
        """Switch to absolute positioning (G90)"""
        comment("Switching to absolute positioning")
        self._grbl.streamLine("G90")

    def rel(self):
        """Switch to relative/incremental positioning (G91)"""
        comment("Switching to relative/incremental positioning")
        self._grbl.streamLine("G91")

    def zero(self):
        """Switch to absolute positioning, and reset origin to current position."""
        comment("Switching to absolute positioning, and reset origin to current position")
        self._grbl.stream(("G90", "G92 X0 Y0 Z0"))

    def stream(self, filename, *args):
        """Stream the specified file to grbl. You can specify absolute path of the file, or name of a file in the gcode folder. You can add somme addition argument fter file name:
     - 'debug':  stream the file step by step
     - 'limit':  try add a Z feed rate limitation
     - 'buffered': use buffered mode to stream the file"""
        if("buffered" in args):
            self._grbl.buffered = True
        if("limit" in args):
            self._grbl.zLimit = True
        if(not filename.startswith("/")):
            filename = os.path.abspath("gcode/%s" % (filename))
        if(os.path.isfile(filename)):
            comment("Start streaming %s file" % filename)
            f = open(filename, 'r')
            try:
                self._grbl.stream(f, "debug" in args)
            except KeyboardInterrupt:
                info("")
                warn("Streaming interrupted. Grbl connection will be reset to stop current processing Job")
                self._grbl.resetConnection()
            f.close()
        else:
            warn("No such file %s" % filename)
        self._grbl.buffered = False
        self._grbl.zLimit = False

    def connect(self, dev=None, bitrate=None):
        """Connect to a grbl/arduino board.
    - dev : device/port to connect to . If not indicated will try to find the device automatically.
    - bitrate : bitrate used by the grbl board to communicate.
        """
        if(bitrate):
            bitrate = int(bitrate)
        if(self._grbl.connect(dev, bitrate)):
            info("Connection initilized")

    def disconnect(self):
        """Close the current serial connection to GRBL"""
        self._grbl.close()

    def reset(self):
        """Reset the current serial connection to GRBL"""
        self._grbl.resetConnection()

    def ls(self):
        """List .ngc files to stream from the gcode filder."""
        for f in os.listdir("gcode"):
            if(f.upper().endswith(".NGC") or f.upper().endswith(".GCODE")):
                info(f)

    def clear(self):
        """Clear console"""
        os.system("clear")

    def status(self):
        """Show grbl status and position. Same as the ? grbl internal command"""
        info(self._grbl.status)

    def help(self, cmd=None):
        """Show this help"""
        if(cmd in dir(self)):
            info(getattr(self, cmd).__doc__)
        else:
            info("""
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
 - 'exit': exit this tool""")
            for m in dir(self):
                if(not m.startswith("_")):
                    info(" - %s: %s" % (m, getattr(self, m).__doc__))
