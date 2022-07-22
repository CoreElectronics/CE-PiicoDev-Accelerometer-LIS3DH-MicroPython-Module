'\nLIS3DH MicroPython Library for PiicoDev\nCreated by Michael Ruppe for Core Electronics (www.core-electronics.com.au)\nProject hosted at https://github.com/CoreElectronics/CE-PiicoDev-Accelerometer-LIS3DH-MicroPython-Module\n\nRequires the PiicoDev Unified Library\nhttps://github.com/CoreElectronics/CE-PiicoDev-Unified\n\nBased on work from from https://github.com/adafruit/Adafruit_CircuitPython_LIS3DH\n\nv1.0.0 rc\n'
_C='little'
_B='big'
_A=None
from PiicoDev_Unified import *
from math import atan2,pi,sqrt
try:from ustruct import pack,unpack;from ucollections import namedtuple
except:from struct import pack,unpack;from collections import namedtuple
_R_WHOAMI=15
_ID=51
_I2C_ADDRESS=25
_OUT_X_L=40
_CTRL_REG_1=32
_CTRL_REG_2=33
_CTRL_REG_3=34
_CTRL_REG_4=35
_CTRL_REG_5=37
_INT1_SRC=49
_CLICK_CFG=56
_CLICKSRC=57
_CLICK_THS=58
_TIME_LIMIT=59
_TIME_LATENCY=60
_TIME_WINDOW=61
_STATUS_REG=39
compat_str='\nUnified PiicoDev library out of date.  Get the latest module: https://piico.dev/unified \n'
AccelerationTuple=namedtuple('acceleration',('x','y','z'))
AngleTuple=namedtuple('angle',('x','y','z'))
def rad2deg(x):return x*180/pi
def _set_bit(x,n):return x|1<<n
def _clear_bit(x,n):return x&~(1<<n)
def _write_bit(x,n,b):
	if b==0:return _clear_bit(x,n)
	else:return _set_bit(x,n)
def _read_bit(x,n):return x&1<<n!=0
def _write_crumb(x,n,c):x=_write_bit(x,n,_read_bit(c,0));return _write_bit(x,n+1,_read_bit(c,1))
def signed_int_from_bytes(x,endian=_B):
	"Return a 16-bit signed integer (from two's complement)";y=int.from_bytes(x,endian)
	if y&32768:y=-(65536-y)
	return y
class PiicoDev_LIS3DH:
	def __init__(self,bus=_A,freq=_A,sda=_A,scl=_A,address=_I2C_ADDRESS,asw=_A,range=2,rate=400):
		try:
			if compat_ind>=1:0
			else:print(compat_str)
		except:print(compat_str)
		if asw not in[0,1]:self.address=_I2C_ADDRESS
		else:self.address=[_I2C_ADDRESS,_I2C_ADDRESS-1][asw]
		self.i2c=create_unified_i2c(bus=bus,freq=freq,sda=sda,scl=scl)
		try:
			if self.deviceID!=_ID:print('Warning device at {} not recognised as LIS3DH'.format(self.address))
			sleep_ms(5);d=7;x=int.to_bytes(d,1,_B);self._write(_CTRL_REG_1,x);d=136;x=int.to_bytes(d,1,_B);self._write(_CTRL_REG_4,x);self.range=range;self.rate=rate
		except Exception as e:print(i2c_err_str.format(self.address));raise e
	@property
	def data_ready(self):d=self._read(_STATUS_REG,1);return _read_bit(d,3)
	@property
	def deviceID(self):'Returns contents of WHO_AM_I register';x=self.i2c.readfrom_mem(self.address,_R_WHOAMI,1);return int.from_bytes(x,_B)
	@property
	def range(self):'Return the accelerometer range [g]';return self._range
	@range.setter
	def range(self,r):
		'Set the range in [g]. Valid ranges are 2, 4, 8, 16';valid_ranges={2:0,4:1,8:2,16:3}
		try:rr=valid_ranges[r]
		except KeyError:raise ValueError('range must be one of 2, 4, 8, or 16')
		val=self._read(_CTRL_REG_4,1);val=_write_crumb(val,4,rr);self._write(_CTRL_REG_4,int.to_bytes(val,1,_B));self._range=r
	@property
	def rate(self):'Return the accelerometer range [g]';return self._rate
	@rate.setter
	def rate(self,r):
		'Set the data rate [Hz]. Valid rates are 1, 10, 25, 50, 100, 200, 400';valid_rates={0:0,1:1,10:2,25:3,50:4,100:5,200:6,400:7}
		try:rr=valid_rates[r]
		except KeyError:raise ValueError('rate must be one of 0, 1, 10, 25, 50, 100, 200, or 400')
		val=self._read(_CTRL_REG_1,1);val&=15;val=val|rr<<4;self._write(_CTRL_REG_1,int.to_bytes(val,1,_C));self._rate=r
	@property
	def acceleration(self):'Return x,y,z acceleration in a 3-tuple. unit: :math:`m/s^2';d=self._read(_OUT_X_L|128,6,bytestring=True);x,y,z=unpack('<hhh',d);divisors={2:1670.295,4:835.1476,8:417.6757,16:139.1912};den=divisors[self.range];x=x/den;y=y/den;z=z/den;return AccelerationTuple(x,y,z)
	@property
	def angle(self):'Return 3-axis tilt angle in degrees';x,y,z=self.acceleration;ay=rad2deg(atan2(z,x));az=rad2deg(atan2(x,y));ax=rad2deg(atan2(y,z));return AngleTuple(ax,ay,az)
	def set_tap(self,tap,threshold=40,time_limit=10,latency=80,window=255,click_cfg=_A):
		if not tap in[0,1,2]:raise ValueError('tap must be 0 (disabled), 1 (single-tap), or 2 (double-tap)')
		if threshold>127 or threshold<0:raise ValueError('threshold out of range (0-127)')
		threshold=threshold|128
		if tap==0 and click_cfg is _A:val=self._read(_CTRL_REG_3,1);val=_clear_bit(val,7);self._write(_CTRL_REG_3,int.to_bytes(val,1,_B));self._write(_CLICK_CFG,b'\x00');return
		if tap==0 and click_cfg is not _A:self._write(_CLICK_CFG,click_cfg)
		ctrl3=self._read(_CTRL_REG_3,1);ctrl3=_set_bit(ctrl3,7);self._write(_CTRL_REG_3,int.to_bytes(ctrl3,1,_B));self._write(_CTRL_REG_5,b'\x08')
		if tap==1:self._write(_CLICK_CFG,b'\x15')
		if tap==2:self._write(_CLICK_CFG,b'*')
		threshold=threshold|128;self._write(_CLICK_THS|128,pack('>BBBB',threshold|128,time_limit,latency,window))
	@property
	def tapped(self):
		raw=self._read(_CLICKSRC,1)
		if raw&64:self._read(_INT1_SRC,1);return True
		return False
	def shake(self,threshold=15,avg_count=40,total_delay=100):
		'Detect when the accelerometer is shaken. Optional parameters:\n        :param int shake_threshold: Increase or decrease to change shake sensitivity.\n                                    This requires a minimum value of 10.\n                                    10 is the total acceleration if the board is not\n                                    moving, therefore anything less than\n                                    10 will erroneously report a constant shake detected.\n                                    Defaults to :const:`20`\n        :param int avg_count: The number of readings taken and used for the average\n                              acceleration. Default to :const:`20`\n        :param int total_delay: The total time in milliseconds it takes to obtain avg_count\n                                  readings from acceleration. Defaults to :const:`100`\n        ';shake_accel=0,0,0
		for _ in range(avg_count):shake_accel=tuple(map(sum,zip(shake_accel,self.acceleration)));sleep_ms(round(total_delay/avg_count))
		avg=tuple((value/avg_count for value in shake_accel));total_accel=sqrt(sum(map(lambda x:x*x,avg)));return total_accel>threshold
	def _read(self,reg,N,bytestring=False):
		try:
			reg|=128;d=self.i2c.readfrom_mem(self.address,reg,N)
			if bytestring:return bytes(d)
			tmp=int.from_bytes(d,_C)
		except:print('Error reading from LIS3DH at address 0x{:02x}'.format(self.address));return float('NaN')
		return tmp
	def _write(self,reg,data):
		try:self.i2c.writeto_mem(self.address,reg,data)
		except:print('Error writing to LIS3DH');return float('NaN')