"""
LIS3DH MicroPython Library for PiicoDev
Created by Michael Ruppe for Core Electronics (www.core-electronics.com.au)
Project hosted at https://github.com/...
Version 1.0 - 10/01/16

Requires the PiicoDev Unified Library
https://github.com/...

Based on work from from https://github.com/mattdy/python-lis3dh
"""

from PiicoDev_Unified import *
from math import atan2, pi
_R_WHOAMI = 0x0F
_ID = 0x33
_I2C_ADDRESS = 24
_OUT_X_L = 0x28
_CTRL_REG_1 = 0x20
_CTRL_REG_2 = 0x21
_CTRL_REG_3 = 0x22
_CTRL_REG_4 = 0x23
_STATUS_REG = 0x27

compat_str = '\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'

def rad2deg(x):
    return x * 180/pi
    
def _setBit(x, n):
    return x | (1 << n)

def _clearBit(x, n):
    return x & ~(1 << n)

def _writeBit(x, n, b):
    if b == 0:
        return _clearBit(x, n)
    else:
        return _setBit(x, n)
    
def _readBit(x, n):
    return x & 1 << n != 0
    
def _writeCrumb(x, n, c):
    x = _writeBit(x, n, _readBit(c, 0))
    return _writeBit(x, n+1, _readBit(c, 1))

def signedIntFromBytes(x, endian='big'):
    """Return a 16-bit signed integer (two's complement)"""
    y = int.from_bytes(x, endian)
    if (y & 0x8000):
        y = - (0x010000 - y)
    return y

class PiicoDev_LIS3DH(object):    
    def __init__(self, bus=None, freq=None, sda=None, scl=None, address=_I2C_ADDRESS, range=2, rate=100):
        try:
            if compat_ind >= 1:
                pass
            else:
                print(compat_str)
        except:
            print(compat_str)

        self.i2c = create_unified_i2c(bus=bus, freq=freq, sda=sda, scl=scl)
        self.addr = address
        
        try:
            if self.deviceID != _ID: print("Warning device at {} not recognised as LIS3DH".format(self.addr))
            sleep_ms(5) # guarantee startup
            # Write basic, unchanging settings to the CTRL_REG1,4
            d = 0x07 # Enable X,Y,Z axes
            x = int.to_bytes(d,1,'big')
            self._write(_CTRL_REG_1, x)
            d=0
            d |= 0x80 # Block Data Update
            d |= 0x08 # High Resolution mode
            x = int.to_bytes(d,1,'big')
            self._write(_CTRL_REG_4, x)
            self.range = range
            self.rate = rate
        except Exception as e:
            print(i2c_err_str.format(self.addr))
            raise e
        
    @property
    def data_ready(self):
        d = self._read(_STATUS_REG, 1)
        return _readBit(d, 3)

    @property
    def deviceID(self):
        """Returns contents of WHO_AM_I register"""
        x=self.i2c.readfrom_mem(self.addr, _R_WHOAMI, 1)
        return int.from_bytes(x,'big')
    
    def self_test(self, st):
        """Self-test 0:disable, 1:enable"""
        val = self._read(_CTRL_REG_4, 1)  # Get value from register
        val = _writeBit(val,1,st)
        self._write(_CTRL_REG_4, int.to_bytes(val,1,'big'))  # Write value back to register

    @property
    def range(self):
        """Return the accelerometer range [g]"""
        return self._range
    @range.setter
    def range(self, r):
        """Set the range in [g]. Valid ranges are 2, 4, 8, 16"""
        if r not in [2,4,8,16]: raise Exception("Invalid range. Must be 2, 4, 8, or 16")
        val = self._read(_CTRL_REG_4, 1)  # Get value from register
        ranges = {2:0b00, 4:0b01, 8:0b10, 16:0b11}
        val = _writeCrumb(val, 4, ranges[r]) # Write new range code
        self._write(_CTRL_REG_4, int.to_bytes(val,1,'big'))
        self._range = r
    
    @property
    def rate(self):
        """Return the accelerometer range [g]"""
        return self._rate
    @range.setter
    def rate(self, r):
        """Set the data rate [Hz]. Valid rates are 1, 10, 25, 50, 100, 200, 400"""
        if r not in [0, 1, 10, 25, 50, 100, 200, 400]: raise Exception("Invalid data rate. Must be 0, 1, 10, 25, 50, 100, 200, 400")
        val = self._read(_CTRL_REG_1, 1)  # Get value from register
        rates = {0:0b0000, 1:0b0001, 10:0b0010, 25:0b0011, 50:0b0100, 100:0b0101, 200:0b0110, 400:0b0111}
        val &= 0x0F # mask off last 4 bits
        val = val | rates[r] << 4
        self._write(_CTRL_REG_1, int.to_bytes(val,1,'big'))
        self._rate = rates[r]
        
    def power_down(self):
        """Power the device down"""
        self.rate=0
    
    def _readAccelRaw(self):
        """Raw register data [signed integer]"""
        d = self._read(_OUT_X_L, 6, True)
        x = signedIntFromBytes(bytes([d[0],d[1]]),'little')
        y = signedIntFromBytes(bytes([d[2],d[3]]),'little')
        z = signedIntFromBytes(bytes([d[4],d[5]]),'little')
        return (x,y,z)
    
    def accel(self, raw=False):
        """Scaled acceleration data"""
        num = self._readAccelRaw()
        if raw: return num
        divisors = {2:16380, 4:8190, 8:4096, 16:1365.33}
        den = divisors[self.range]
        return num[0]/den, num[1]/den, num[2]/den
    
    def angle(self, unit='radians'):
        x,y,z = self._readAccelRaw()
        xz = atan2(x,z)
        xy = atan2(x,y)
        yz = atan2(y,z)
        if unit == 'degrees':
            return rad2deg(xz), rad2deg(xy), rad2deg(yz)
        else:
            return xz, xy, yz

    def _read(self, reg, N, bytestring=False):
        try:
            reg |= 0x80 # bit 7 enables address auto-increment (crazy, esoteric feature specific to LIS3DH)
            d = self.i2c.readfrom_mem(self.addr, reg, N)
            if bytestring: return d
            tmp = int.from_bytes(d, 'little')
        except:
            print("Error reading from LIS3DH at address 0x{:02x}".format(self.addr))
            return float('NaN')
        return tmp
        
    def _write(self, reg, data):
        try:
            self.i2c.writeto_mem(self.addr, reg, data)
        except:
            print("Error writing to LIS3DH")
            return float('NaN')
