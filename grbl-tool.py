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


import argparse, sys
import readline
from lib.utils import *
from lib.grbl import *
import lib.macros
import webbrowser

cli_startup = """
=================== Command line mode ===================

You can manually send commands to grbl that can be :
 - '$' to show current grbl settings
 - '$x=value' to set a parameter
 - 'exit' to exit this tool
 - 'help' to show more help

=========================================================
"""


class WebApp(threading.Thread):
    def __init__(self):
        super(WebApp, self).__init__()
        self.daemon = True
        self.start()

    def run(self):
        from gevent.pywsgi import WSGIServer
        from geventwebsocket.handler import WebSocketHandler
        import web
        http_server = WSGIServer(("127.0.0.1", 8000), web.webapp, handler_class=WebSocketHandler)
        http_server.serve_forever()

def main():
    global args
    parser = argparse.ArgumentParser(description='Tool to stream GCODE to a GRBL driver machine.')
    parser.add_argument('-v', '--verbose', action="store_true", help='Verbose output, Show more informations')
    parser.add_argument('-q', '--quiet', action="store_true", help='Force no output,even if verbose mode is active')
    parser.add_argument('-d', '--device', nargs='?', default=None, help='Serila device to be used. If none defined, it will try to find it automaticaly.')
    parser.add_argument('--bitrate', nargs='?', default=None, help='Serial device to be used. If none defined, it will try to find it automaticaly.')
    parser.add_argument('--gui', action="store_true", help='Start grbl tool with  a graphical user interface an not a console interface.')
    parser.add_argument('--debug', action="store_true", help='Start grbl tool with  a graphical user interface an not a console interface.')
    parser.add_argument('-s', '--stream', nargs='?', type=argparse.FileType('r'), default=None, help='Input file to be parsed, if not specified tool will be launch as a manual command line interface')
    try :
        args = parser.parse_args()
    except IOError :
        sys.exit(0)
    if args.gui :
        if args.debug :
            print "starting GUI in debug mode"
            start_debug_gui()
        else:
            print "starting GUI"
            start_gui()
    else:
        start_cli()

def start_debug_gui():
    WebApp()
    webbrowser.get('firefox').open("http://localhost:8000/")
    line = raw_input("Enter to exit ")
    # os.system("firefox -app firefox-app/application.ini -jsconsole")



def start_gui():
    WebApp()
    os.system("firefox -app firefox-app/application.ini")

def start_cli():
    pathname = os.path.dirname(sys.argv[0])  # current script's path
    if(os.path.isfile(os.path.join(pathname, ".history"))):
        readline.read_history_file(os.path.join(pathname, ".history"))

    # Initialize
    print cli_startup
    grbl = Grbl(args.device, args.bitrate)
    macro = lib.macros.Macro(grbl)
    macro.connect(args.device, args.bitrate)
    try :
        if(args.stream == None):
            while True:
                line = raw_input(" ~ ")
                if(line.strip().upper() == "EXIT"):
                    info("Exiting ...")
                    break;
                else:
                    grbl.processCommand(macro, line)
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
    readline.write_history_file(os.path.join(pathname, ".history"))


if __name__ == "__main__":
    sys.exit(main())
