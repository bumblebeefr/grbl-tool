from lib.utils import comment, debug, info, warn, log_out, log_in
import os
import time
import math
import re
import serial
import threading
from Queue import Queue
from time import sleep
from parse import parse
from serial.serialutil import SerialException
import events

STATUS_MOTIF = '<{status},MPos:{machine.x:g},{machine.y:g},{machine.z:g},WPos:{work.x:g},{work.y:g},{work.z:g}>'


class GrblSerialReader(threading.Thread):
    def __init__(self, grbl):
        super(GrblSerialReader, self).__init__()
        self.grbl = grbl
        self.daemon = True
        self.start()

    def storeStatus(self, status):
        if self.grbl.status != status:
            events.trigger("status", status)
        self.grbl.status = status

    def sendOutput(self, output):
        if(output.get('status', '') == 'ok' and output.get('text', []) and output.get('text')[0]):
            grbl_status = parse(STATUS_MOTIF, output['text'][0])
            if grbl_status != None:
                self.storeStatus(grbl_status.named)
                return
        self.grbl.command_output_queue.put(output)

    def run(self):
        try:
            output = {'status': "ok", 'text': []}
            while True:
                if(not self.grbl.serial):
                    return
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
        except SerialException as e:
            self.grbl._serial_error(e)


class GrblStatusManager(threading.Thread):
    def __init__(self, grbl):
        super(GrblStatusManager, self).__init__()
        self.grbl = grbl
        self.daemon = True
        self.start()

    def run(self):
        try:
            while True:
                if(self.grbl.status.get('status', None) != 'Idle' or self.grbl.running):
                    if(self.grbl.status.get('status', None) == 'Idle'):
                        self.grbl.running = False
                    if self.grbl.serial:
                        self.grbl.serial.write('?\n')
                    else:
                        return
                sleep(0.2)
        except SerialException as e:
            self.grbl._serial_error(e)


class Grbl:
    """ Class that wrap a serial connection to a grbl instance and allow to stream Gcode commande to GRBL CNC. """

    def __init__(self, device=None, bitrate=9600):
        self.serial = None
        self.bitrate = None
        self.default_bitrate = bitrate
        self.running = False
        self.status = {}
        self.connected = False

        self.l_count = 0
        self.g_count = 0
        self.c_line = []

        self.defaultSpeed = 500
        self.zSpeed = 150
        self.zLimit = False

        self.command_output_queue = Queue()

    def _serial_error(self, e):
            warn("Serial communication error, you should reconnect : %s" % e)
            events.trigger("serial.disconnected")
            if(self.serial):
                try:
                    self.serial.close()
                except SerialException:
                    self.serial = None
            self.serial = None
            self.connected = False
            self.status = {}

    def __initializeSerialPort(self, dev, bitrate):
        """Try to initalise a Serial connection to the specified device. Return the  device if we are connected to a valid Grbl device, None otherwise. """
        debug("Initializing grbl connection to %s ..." % dev)
        try:
            s = serial.Serial(dev, bitrate)
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
                self.bitrate = bitrate
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

    def connect(self, device=None, bitrate=None):
        """
        Connect to the specified grbl/arduino board.
        If no device specied, of if the specified device connection fail, it will try to fin the correct device/port.
        (auto detection does not work on windows platform yet).
        """
        if(device != None):  # try to find an arduino tty connection (only *nux os supported) //TODO try initate grbl com in case of multiple usbtty
            if(bitrate):
                self.serial = self.__initializeSerialPort(device, bitrate)
            else:
                self.serial = self.__initializeSerialPort(device, self.default_bitrate)

        if(self.serial == None):
            for f in os.listdir("/dev/"):
                if(f.find("ttyUSB") == 0 or f.find("ttyACM") == 0):
                    dev = "/dev/" + f
                    if(bitrate):
                        self.serial = self.__initializeSerialPort(dev, bitrate)
                    else:
                        self.serial = self.__initializeSerialPort(dev, self.default_bitrate)
                    if (self.serial != None):
                        self.connected = True
                        break
        if(self.serial == None):
            warn("Unable to connect to a Grbl device")
            events.trigger("serial.disconnected")
            return False
        else:
            self.serial_reader = GrblSerialReader(self)
            self.serial_status_manager = GrblStatusManager(self)
            events.trigger("serial.connected", {"port": self.serial.getPort(), "bitrate": self.bitrate})
            return True

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
        if self.serial :
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
            return output
        else:
            warn("Not connected to GRBL board.")

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
            return self.sendLine(line)
        elif(len(line.strip()) > 0):
            comment(line.strip())

    def processCommand(self, macro, strCmd):
        try:
            strCmd = strCmd.strip()
            cmdSplit = strCmd.split(" ")
            if(hasattr(macro, cmdSplit[0])):
                debug("Command found")
                args = cmdSplit[1:]
                try:
                    return getattr(macro, cmdSplit[0])(*args)
                except TypeError, e:
                    warn("Error  :%s" % e)
            elif(hasattr(macro, macro._alias.get(cmdSplit[0], ""))):
                debug("Command found")
                args = cmdSplit[1:]
                try:
                    return getattr(macro, macro._alias.get(cmdSplit[0], ""))(*args)
                except TypeError, e:
                    warn("Error  :%s" % e)
            elif (not self.isComment(strCmd)):
                return self.streamLine(strCmd)
        except SerialException as e:
            self._serial_error(e)

    def close(self):
        if(self.serial):
            self.serial.close()

    def resetConnection(self):
        if(self.serial):
            self.serial.close()
            self.running = False
            self.serial.open()
            time.sleep(2)
            self.serial.flushInput()
        else:
            warn("Not connected to GRBL board.")
