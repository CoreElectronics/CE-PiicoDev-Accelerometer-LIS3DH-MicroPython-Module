"""
PiicoDev Accelerometer LIS3DH
Simple example to detect single or double-tapping.
See the docs for for information on configuring .set_tap()
https:// [ToDo insert link]
"""
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function
from machine import Pin
led = Pin(25, Pin.OUT)
ledState = True

motion = PiicoDev_LIS3DH()

motion.set_tap(2)

while True:
    print("")
    if motion.tapped:
        print('tapped')
    sleep_ms(2000)
