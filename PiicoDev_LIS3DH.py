"""
LIS3DH MicroPython Library for PiicoDev
Created by Michael Ruppe for Core Electronics (www.core-electronics.com.au)
Project hosted at https://github.com/...
Version 1.0 - 2022-06-26

Requires the PiicoDev Unified Library
https://github.com/...

Based on work from from https://github.com/adafruit/Adafruit_CircuitPython_LIS3DH
"""

from PiicoDev_Unified import *
from math import atan2, pi, sqrt
# ToDo: branch for struct and ustruct etc.
from ustruct import pack, unpack
from ucollections import namedtuple
_R_WHOAMI = 0x0F
_ID = 0x33
_I2C_ADDRESS = 24
_OUT_X_L = 0x28
_CTRL_REG_1 = 0x20
_CTRL_REG_2 = 0x21
_CTRL_REG_3 = 0x22
_CTRL_REG_4 = 0x23
_CTRL_REG_5 = 0x25
_INT1_SRC = 0x31
_CLICK_CFG = 0x38
_CLICKSRC = 0x39
_CLICK_THS = 0x3A
_TIME_LIMIT = 0x3B
_TIME_LATENCY=0x3C
_TIME_WINDOW = 0x3D
_STATUS_REG = 0x27

compat_str = '\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'

AccelerationTuple = namedtuple("acceleration", ("x", "y", "z"))

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
    """Return a 16-bit signed integer (from two's complement)"""
    y = int.from_bytes(x, endian)
    if (y & 0x8000):
        y = - (0x010000 - y)
    return y

class PiicoDev_LIS3DH(object):    
    def __init__(self, bus=None, freq=None, sda=None, scl=None, address=_I2C_ADDRESS, range=2, rate=400):
        try:
            if compat_ind >= 1: pass
            else: print(compat_str)
        except: print(compat_str)

        self.i2c = create_unified_i2c(bus=bus, freq=freq, sda=sda, scl=scl)
        self.addr = address
        
        try:
            if self.deviceID != _ID: print("Warning device at {} not recognised as LIS3DH".format(self.addr))
            sleep_ms(5) # guarantee startup
            # Write basic, unchanging settings to the CTRL_REG1,4
            d = 0x07 # Enable X,Y,Z axes
            x = int.to_bytes(d,1,'big')
            self._write(_CTRL_REG_1, x)
            d = 0x88 # Block Data Update an High Resolution Mode
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
    
    @property
    def range(self):
        """Return the accelerometer range [g]"""
        return self._range
    
    @range.setter
    def range(self, r):
        """Set the range in [g]. Valid ranges are 2, 4, 8, 16"""
        valid_ranges = {2:0b00, 4:0b01, 8:0b10, 16:0b11} # key:value -> range[g] : binary code for register
        try: rr = valid_ranges[r]
        except(KeyError): raise ValueError("range must be one of {}".format(r, list(valid_ranges.keys())))
        val = self._read(_CTRL_REG_4, 1)
        ranges = {2:0b00, 4:0b01, 8:0b10, 16:0b11}
        val = _writeCrumb(val, 4, rr) # Write new range code
        self._write(_CTRL_REG_4, int.to_bytes(val,1,'big'))
        self._range = r
    
    @property
    def rate(self):
        """Return the accelerometer range [g]"""
        return self._rate
    
    @range.setter
    def rate(self, r):
        """Set the data rate [Hz]. Valid rates are 1, 10, 25, 50, 100, 200, 400"""
        valid_rates = {0:0b0000, 1:0b0001, 10:0b0010, 25:0b0011, 50:0b0100, 100:0b0101, 200:0b0110, 400:0b0111} # key:value -> rate[Hz] : binary code for register
        try: rr = valid_rates[r]
        except(KeyError): raise ValueError("rate must be one of {}".format(r,valid_rates))
        val = self._read(_CTRL_REG_1, 1)  # Get value from register
        val &= 0x0F # mask off last 4 bits
        val = val | rr << 4
        self._write(_CTRL_REG_1, int.to_bytes(val,1,'little'))
        self._rate = r
    
    @property
    def acceleration(self):
        """Return x,y,z acceleration in a 3-tuple. unit: :math:`m/s^2"""
        d = self._read(_OUT_X_L | 0x80, 6, bytestring=True)
        x,y,z = unpack('<hhh', d)
        divisors = {2:1670.295, 4:835.1476, 8:417.6757, 16:139.1912} # (LSB/1g) / 9.80665
        den = divisors[self.range]
        x = x/den; y=y/den; z=z/den;
        return AccelerationTuple(x, y, z)
        
    @property    
    def angle(self):
        """Return 3-axis tilt angle in degrees"""
        x,y,z = self.acceleration
        xz = atan2(x,z)
        xy = atan2(x,y)
        yz = atan2(y,z)
        return rad2deg(xz), rad2deg(xy), rad2deg(yz)

    def set_tap(self, tap, threshold=40, time_limit=10, latency=80, window=255, click_cfg=None):
        if not tap in [0,1,2]:
            raise ValueError("tap must be 0 (disabled), 1 (single-tap), or 2 (double-tap)")
        if threshold > 127 or threshold < 0:
            raise ValueError("threshold out of range (0-127)")
        threshold = threshold | 0x80
        if tap == 0 and click_cfg is None: # disable click interrupt
            val = self._read(_CTRL_REG_3,1)
            val = _clearBit(val,7) # disable INT1 CLICK
            self._write(_CTRL_REG_3, int.to_bytes(val,1,'big'))
            self._write(_CLICK_CFG, b'\x00') # disable all click detection
            return
        ctrl3 = self._read(_CTRL_REG_3,1)
        ctrl3 = _setBit(ctrl3,7) # Enable INT1 CLICK
        self._write(_CTRL_REG_3, int.to_bytes(ctrl3,1,'big'))
        self._write(_CTRL_REG_5, b'\x08') # Latch INT1
        
        # Could use dict, similar to range and rate properties
        if tap == 1:
            self._write(_CLICK_CFG, b'\x15') # enable single tap on all axes
        if tap == 2:
            self._write(_CLICK_CFG, b'\x2A') # enable double tap on all axes
        
        # write timing parameters
        threshold = threshold | 0x80 # latch interrupt until CLK_SRC is read
        self._write(_CLICK_THS | 0x80, pack('>BBBB', threshold | 0x80, time_limit, latency, window))
        
    @property
    def tapped(self):
        raw = self._read(_CLICKSRC,1)
        if raw & 0x40:
            self._read(_INT1_SRC,1) # clear interrupt pin
            return True
        return False
    
    def shake(self, shake_threshold=20, avg_count=20, total_delay=100):
        """Detect when the accelerometer is shaken. Optional parameters:
        :param int shake_threshold: Increase or decrease to change shake sensitivity.
                                    This requires a minimum value of 10.
                                    10 is the total acceleration if the board is not
                                    moving, therefore anything less than
                                    10 will erroneously report a constant shake detected.
                                    Defaults to :const:`20`
        :param int avg_count: The number of readings taken and used for the average
                              acceleration. Default to :const:`20`
        :param int total_delay: The total time in milliseconds it takes to obtain avg_count
                                  readings from acceleration. Defaults to :const:`100`
        """

        shake_accel = (0, 0, 0)
        for _ in range(avg_count):
            # shake_accel creates a list of tuples from acceleration data.
            # zip takes multiple tuples and zips them together, as in:
            # In : zip([-0.2, 0.0, 9.5], [37.9, 13.5, -72.8])
            # Out: [(-0.2, 37.9), (0.0, 13.5), (9.5, -72.8)]
            # map applies sum to each member of this tuple, resulting in a
            # 3-member list. tuple converts this list into a tuple which is
            # used as shake_accel.
            shake_accel = tuple(map(sum, zip(shake_accel, self.acceleration)))
            sleep_ms(round(total_delay / avg_count))
        avg = tuple(value / avg_count for value in shake_accel)
        total_accel = sqrt(sum(map(lambda x: x * x, avg)))
        print(total_accel, shake_threshold)
        return total_accel > shake_threshold

    def _read(self, reg, N, bytestring=False):
        try:
            reg |= 0x80 # bit 7 enables address auto-increment (esoteric feature specific to LIS3DH)
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
