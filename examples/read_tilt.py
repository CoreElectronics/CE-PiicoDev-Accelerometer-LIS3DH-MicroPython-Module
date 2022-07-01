"""
PiicoDev Accelerometer LIS3DH
Simple example to infer tilt-angle from acceleration data
"""

from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function

motion = PiicoDev_LIS3DH()

while True:
    xz, xy, yz = motion.angle # Tilt could be measured with respect to three different axes
    print("Angle: {:.0f}°".format(yz)) # Print the angle with respect to the Y-Z axis
    sleep_ms(50)
    