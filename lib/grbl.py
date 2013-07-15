from lib.utils import *
import os
import sys
import time
import math
import re
import serial
import threading
from Queue import Queue, Empty
from time import sleep

class GrblSerialReader(threading.Thread):
    def __init__(self, grbl):
        super(GrblSerialReader, self).__init__()
        self.grbl = grbl
        self.daemon = True
        self.start()

    def sendOutput(self, output):
        if(output.get('status', '') == 'ok' and output.get('text', [])):
            if(output['text'][0][0] == '<' and output['text'][0][-1] == '>'):
                self.grbl.status = output['text'][0]
                return
        self.grbl.command_output_queue.put(output)

    def run(self):
        output = {'status': "ok", 'text': []}
        while True:
            tmp = self.grbl.serial.readline().strip()
            if(tmp[:5] in ('ok', 'error')):
                if(tmp == 'ok'):
                    output['status'] = tmp
                else:
                    output['status'] = 'error'
                    output['text'].append(tmp)
                self.sendOutput(output)
                output = {'status': "ok", 'text': []}
            else:
                output['text'].append(tmp)

class GrblStatusManager(threading.Thread):
    def __init__(self, grbl):
        super(GrblStatusManager, self).__init__()
        self.grbl = grbl
        self.daemon = True
        self.start()

    def run(self):
        output = {'status': "ok", 'text': []}
        while True:
            self.grbl.serial.write('?\n')
            sleep(0.1)


class Grbl:
    """ Class that wrap a serial connection to a grbl instance and allow to stream Gcode commande to GRBL CNC. """

    def __init__(self, device, bitrate, buffered):
        self.serial = None
        self.bitrate = bitrate
        self.running = False
        self.status = ""

        self.l_count = 0
        self.g_count = 0
        self.c_line = []

        self.defaultSpeed = 500
        self.zSpeed = 150
        self.zLimit = False

        self.command_output_queue = Queue()
        self.status_queue = Queue()

        self.lastPosition = [0, 0, 0, 0]

        if(device != None):  # try to find an arduino tty connection (only *nux os supported) //TODO try initate grbl com in case of multiple usbtty
            self.serial = self.__initializeSerialPort(device)
        if(self.serial == None):
            for f in os.listdir("/dev/"):
                if(f.find("ttyUSB") == 0 or f.find("ttyACM") == 0):
                    dev = "/dev/" + f
                    self.serial = self.__initializeSerialPort(dev)
                    if (self.serial != None):
                        break
        if(self.serial == None):
            warn("Unable to connect to a Grbl device")
            exit(1)
        else:
            self.serial_reader = GrblSerialReader(self)
            self.serial_status_manager = GrblStatusManager(self)

    def __initializeSerialPort(self, dev):
        """Try to initalise a Serial connection to the specified device. Return the  device if we are connected to a vlaid Grbl device, None otherwise. """
        debug("Initializing grbl connection to %s ..." % dev)
        try:
            s = serial.Serial(dev, self.bitrate)
            # Wake up grbl
            s.write("\r\n\r\n")
            initialized = None
            s.timeout = 0
            time.sleep(2)
            for i in range(4):
                val = s.readline()
                i = i
                if("GRBL" in val.upper()):
                    initialized = val
                    break
            if(initialized != None):
                info("Connected on %s: %s" % (dev, initialized))
                s.timeout = None
                s.flushInput()
                self.device = dev
                return s
            else:
                debug("%s seams not to be a valid grbl connection" % dev)
                return None
        except serial.serialutil.SerialException, e:
            debug("Unable to connect to device %s: %s" % (dev, e))

    def __clean_line(self, line):
        line = line.strip().upper()
        # add a speed ig G0 on Z axis and no speed ed
        # if(re.match("G00.*Z[\-0-9\.]+.*",line.strip().upper() )and not re.match("G00.*F[\-0-9\.]+.*",line.strip().upper())):
        #     comment("Adding 'F100' for Z movement")
        #     line +=" F100"
        if(self.zLimit):
            if(line.startswith("G1 ") or line.startswith("G0 ") or line.startswith("G01") or line.startswith("G00") or line.startswith("X") or line.startswith("Y") or line.startswith("Z")):
                line = self._limitZSpeed(line)
        return line.strip()

    def _getValue(self, line, k):
        a = re.findall(k + "[\\-0-9\\.]*", line)
        if(len(a) > 0):
            return float(a[0][1:])
        else:
            return 0

    def _limitZSpeed(self, line):
        position = [self._getValue(line, "X"), self._getValue(line, "Y"), self._getValue(line, "Z"), self._getValue(line, "F")]
        x = position[0] - self.lastPosition[0]
        y = position[1] - self.lastPosition[1]
        z = position[2] - self.lastPosition[2]
        f = position[3]
        # debug("Translation %s %s %s %s"%(x,y,z,f))
        if(f == 0):
            f = self.defaultSpeed
        if(z != 0):
            v = self.zSpeed * math.sqrt(x ** 2 + y ** 2 + z ** 2) / abs(z)
            # debug("Compurted speed %s" %v)
            if (v < f):
                comment("Z speed limit detected, auto reducing feed rate")
                line = re.sub("F[0-9\\.]*", "", line)  # Suppress 'F' elements
                line = "%s F%.4f" % (line, v)  # Add corrected Feed Rate
        position[3] = f
        self.lastPosition = position
        return line

    def sendLine(self, line):
        l_block = self.__clean_line(line)
        log_out(l_block)
        self.serial.write(l_block + '\n')  # Send block to grbl
        output = self.command_output_queue.get()
        if(output.get('status', None) == 'ok'):
            for txt in output.get('text', []):
                log_in(txt)
            log_in('ok')
        else:
            for txt in output.get('text', []):
                warn(txt)

#         while True:
#             out_temp = self.serial.readline().strip()
#             if (out_temp.find('ok') != -1):
#                 log_in(out_temp)
#                 break
#             elif (out_temp.find('error') != -1):
#                 warn(out_temp)
#                 break
#             else:
#                 log_in(out_temp)

    def stream(self, lines, debug=False, delay=0):
        try:
            for line in lines:
                self.streamLine(line)
                time.sleep(0.01)
                if debug:
                    raw_input("")
        except KeyboardInterrupt:
            print
            warn("Streaming interrupted. Grbl connection will be reset to trop current processing Job")
            self.resetConnection()

    def isComment(self, gcode):
        gcode = gcode.strip()
        return gcode.startswith("%") or len(gcode) == 0 or (gcode.startswith("(") and gcode.endswith(")"))

    def streamLine(self, line):
        self.running = True
        if(not self.isComment(line.strip())):
            self.sendLine(line)
        elif(len(line.strip()) > 0):
            comment(line.strip())

    def close(self):
        self.serial.close()

    def resetConnection(self):
        self.serial.close()
        self.running = False
        self.serial.open()
        time.sleep(2)
        self.serial.flushInput()
