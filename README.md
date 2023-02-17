# PiicoDev® 3-Axis Accelerometer LIS3DH MicroPython Module

This is the firmware repo for the [Core Electronics PiicoDev® 3-Axis Accelerometer LIS3DH MicroPython Module](https://core-electronics.com.au/catalog/product/view/sku/CE08705)

This module depends on the [PiicoDev Unified Library](https://github.com/CoreElectronics/CE-PiicoDev-Unified), include `PiicoDev_Unified.py` in the project directory on your MicroPython device.


# Function reference

### `PiicoDev_LIS3DH(bus=None, freq=None, sda=None, scl=None, address=_I2C_ADDRESS, asw=None, range=2, rate=400)`
Initialisation function.

|Parameter   | Type   | Range             | Default | Description |
|----------- | ------ | ----------------- | ------- | ----------- |
|bus           | int | 0, 1 |         | I2C bus number to use|
|freq           | int  | 100 to 1000000      |         |I2C bus frequency (Hz). Ignored on Raspberry Pi SBC |
|sda | machine.Pin | | Dev. Board dependent |  Explicitly define the I2C bus pins
|scl           | machine.Pin    |           |  Dev. Board dependent      | Explicitly define the I2C bus pins
|address | int |  | 0x19 | Used to explicitly define the I2C address of the Accelerometer
|asw           | int    | 0 or 1          | |  Set the address of the device by encoding the address switch position. The user does not need to know the actual I2C address this way.         |


### `.deviceID`
Returns the contents of the WHO_AM_I register (0x33)

### `.data_ready`
Returns True if a new sample is ready to read.

### `.range`
Set or read the range in g. Valid values are 2,4,8 and 16

### `.rate`
Set or read the sample rate in Hz. Valid rates are 1, 10, 25, 50, 100, 200, 400.

### `.acceleration`
Returns a tuple the acceleration tuple (x,y,z) [m/s^2]

### `.angle`
Returns the 3-axis tilt angle in degrees. Tilt is calculated using atan2 from the acceleration vectors.

### `.set_tap(tap, threshold=40, time_limit=10, latency=80, window=255, click_cfg=None)`
Configure tap detection

|Parameter   | Type   | Range             | Default | Description                            |
|----------- | ------ | ----------------- | ------- | ----------- |
|tap         | int    | 0, 1, 2           |         | Disabled:0, Single-tap:1, Double-tap:2 |
| threshold  | int    | 0-127             | 40      | Tap magnitude threshold                |
|time_limit  | int    |                   | 10      | The maximum time a tap may be above the threshold. |
| latency    | int    |                   | 80      | The 'dead time' between taps |
| window     | int    |                   | 255      | the maximum time window for a double-tap |

### `.tapped`
Returns True when a tap event occurred

### '.shake(threshold=15, avg_count=40, total_delay=100)`
|Parameter   | Type   |  Default | Description                            |
|----------- | ------ |  ------- | ----------- |
| threshold  | int    | 15      | How strong the shaking needs to be |
| avg_count  | int    | 40      | How many samples to average                |
| total_delay| int    |  100     | The total time during which to sample for shaking.

# License
This project is open source - please review the LICENSE.md file for further licensing information.

If you have any technical questions, or concerns about licensing, please contact technical support on the [Core Electronics forums](https://forum.core-electronics.com.au/).

*\"PiicoDev\" and the PiicoDev logo are trademarks of Core Electronics Pty Ltd.*
