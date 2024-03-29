#!/usr/bin/env python

import getopt
import sys
import board
import busio
import adafruit_24lc32
from ina219 import INA219, DeviceRangeError
import time

# R020
SHUNT = 0.02 # [Ohm]
# ???
MAX_CURRENT = 1.0 # [A]

VERSION = """0.1.0
(c) 2024 rstephan, GPL 2 only"""

USAGE = """Usage:
hatdrive.py <options> meter|eeprom

  -h, --help      Show help
  -v, --version   Show version
  -t, --type <t>  Type of HAT
                  top       HatDrive! Top (default)
                  bottom    HatDrive! Bottom
                  ws        Waveshare PCIe TO M.2 HAT+
  -m, --mode <m>  Set output mode
                  0: line-by-line
                  1: single line
                  2: CSV
                  3: CSV with header
  -p, --power     Show power in [mW]
  -q, --quit      Quiet
  -d, --delay <d> Delay between two reading [s]. (def. 0.25)

  meter:
  Show voltage [V] and current [mA] of the HatDrive! continuously.
  
  eeprom:
  Show the content of the 24C32 EEPROM (4kB) as hex-dump.
"""


class HdtMeter:
    mLastLen = 0
    mVolt = 0
    mCurrent = 0
    mWithPower = False
    mIna = None

    def Init(self, bus):
        ina = INA219(SHUNT, MAX_CURRENT, busnum=bus)
        ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)
        self.mIna = ina

    def InaRead(self):
        try:
            self.mVolt = self.mIna.voltage()
            self.mCurrent = self.mIna.current()
            return True
        except DeviceRangeError:
            return None

    def Output(self, mode):
        if mode == 0:
            print("{:.2f} V {:.1f} mA".format(self.mVolt, self.mCurrent), end="")
            if self.mWithPower:
                print(" {:.0f} mW".format(self.mVolt * self.mCurrent), end="")
            print()
        elif mode == 1:
            if self.mLastLen > 0:
                print("{}\r".format(" "*self.mLastLen), end="")
            out = "{:.2f} V {:.1f} mA".format(self.mVolt, self.mCurrent)
            if self.mWithPower:
                out += " {:.0f} mW".format(self.mVolt * self.mCurrent)
            out += "\r"
            self.mLastLen = len(out)
            print(out, end="")
            sys.stdout.flush()
        elif mode == 2 or mode == 3:
            print("{:.2f},{:.1f}".format(self.mVolt, self.mCurrent), end="")
            if self.mWithPower:
                print(",{:.0f}".format(self.mVolt * self.mCurrent), end="")
            print()
        else:
            print("??")


def HdtReadMeter(delay, mode, power, type):
    bus = 0
    if type == "bottom" or type == "ws":
        bus = 1
    meter = HdtMeter()
    meter.Init(bus)
    meter.mWithPower = power
    if mode == 3:
        print("\"HatDriveTool\",\"Meter\"")
        print("\"Voltage [V]\",\"Current [mA]\"", end="")
        if meter.mWithPower:
            print(",\"Power [mW]\"", end="")
        print()
    while True:
        ret = meter.InaRead()
        if not ret is None:
            meter.Output(mode)
            time.sleep(delay)
        else:
            break


def HexDump(data):
    cnt = 0
    for b in data:
        if cnt != 0 and cnt % 16 == 0:
            print()
        if cnt % 16 == 0:
            print("{:04X}: ".format(cnt), end="")
        if cnt % 16 == 8:
            print("- ", end="")
        print("{:02X} ".format(b), end="")
        cnt = cnt + 1
    print()


def HdtEeprom(type):
    addr = 0x50
    if type == "top":
        i2c = busio.I2C(board.D1, board.D0)
    elif type == "bottom":
        i2c = board.I2C()
    elif type == "ws":
        i2c = busio.I2C(board.D1, board.D0)
        addr = 0x51
    else:
        print("Unknown type!")
        return
    eeprom = adafruit_24lc32.EEPROM_I2C(i2c, address=addr)

    print("Size: {}".format(len(eeprom)))
    HexDump(eeprom[:])


def main():
    delay = 0.25
    mode = 0
    quiet = False
    withPower = False
    filename = ""
    type = "top"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:Dd:m:t:qpv",
            ["help", "version", "file=", "debug", "mode=", "delay", "quiet", "power", "type="])
    except getopt.GetoptError as err:
        print(USAGE)
        sys.exit(1)

    #print([opts, args])
    for o, a in opts:
        if o in ("-v", "--version"):
            print(VERSION)
            sys.exit(1)
        if o in ("-h", "--help"):
            print(USAGE)
            sys.exit(1)
        if o in ("-d", "--delay"):
            delay = float(a)
        if o in ("-m", "--mode"):
            mode = int(a)
        if o in ("-q", "--quiet"):
            quiet = True
        if o in ("-p", "--power"):
            withPower = True
        if o in ("-f", "--file"):
            filename = a
        if o in ("-t", "--type"):
            if a == "top" or a == "bottom" or a == "ws":
                type = a
            else:
                print("Unknown type: {}", a)
                sys.exit(1)

    if not quiet:
        print("HatDrive! Tool")

    if len(args) == 1:
        if args[0] == "meter":
            HdtReadMeter(delay, mode, withPower, type)
        elif args[0] == "eeprom":
            HdtEeprom(type)
        else:
            print("Unknown command {}".format(args[0]))


if __name__ == "__main__":
    main()
