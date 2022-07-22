"""
PiicoDev Accelerometer LIS3DH
Simple example to configure single-tap detection.
"""
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function

motion = PiicoDev_LIS3DH()
motion.set_tap(1, threshold=40) # set up single-tap detection with a tap threshold of 40

while True:
    if motion.tapped:
        print(1)
    else:
        print(0)

    sleep_ms(2000)
