# Light Monitor

A Raspberry Pi Pico &amp; MicroPython driven system that measures the intensity of light using LDR sensors and an displays data OLED display. It has since been expanded to also measure temperature and relative humidity.

![License](https://img.shields.io/badge/License-GPL3.0-blue)

A small project used to measure the intensity of light using a Raspberry Pi Pico and two adjustable LDRs written in MicroPython. The system uses two LDR sensors for redundancy and displays relevant information on a small oled screen. It uses a single KY-015 temperature and humidity sensor to measure the temperature and relative humidity.

It can be powered via a micro-usb cable and 5v power supply or via rechargeable lithium ion battery.

## Installation and Use

All that is needed to "install" is to copy the main.py and LIS_display.py files onto the Pico device. This can be done any number of ways, but I used the Thonny editor when designing and testing which made things easy as files can be saved directly to the device memory through it.

To use the system all you need to do is power the Pico device on. As the controller file is named main.py, it should start automatically. To avoid it from running at power on, rename the file to something else, e.g., LIS_driver.py.

For a reference to the pico, sensor, and displays connections, refer to the connectionLayoutVisual.png file in the root directory of this project.

NOTE: The sensors are meant to point in the same direction to get the best readings possible. If they are pointing in different directions, the data will likely be marked invalid as the readings will be outside of the maximum allowed delta.

## Additional Libraries

The [micropython_ssd1306](https://github.com/stlehmann/micropython-ssd1306) is used to communicate with the OLED display. In Thonny with the Pico device plugged into a computer, click "Tools > Manage Packages..." then search for micropython_ssd1306 and install it to the device.

The [dht](https://docs.micropython.org/en/latest/esp32/quickref.html#dht-driver) library is used to interface with the DHT11 sensor used in the project. It comes pre-packaged with the MicroPython library.

## Display Data Explained

There are three types of data collected by the system, light intensity, temperature (in degrees Fahrenheit), and relative humidity.

Light Intensity is measured via two LDR sensors, with one reading coming from each sensor.

Temperature and humidity are measured using a DHT11 sensor. It is important to keep in mind that this sensor is unable to take measurements less than one second from the last so the data frefresh period is limited to timings greater than one second.

The following values are displayed on the display:

| Value Name | Value Description |
|------------|-------------------|
| S1 | Value read from the first LDR sensor. |
| S2 | Value read from the second LDR sensor. |
| Avg. | Average of the two LDR values. |
| R delta | Absolute value of the difference between the two values. |
| % delta | Difference between the two values as a percentage. |
| Valid | Is the % delta between the two values within the acceptable range? |
| Temp. F | Temperature in degrees Fahrenheit. |
| Humidity | Relative humidity as a percentage. |

## Future

Once the system is stable, it would be cool to rewrite the entire thing in C using the Pico SDK. Could be used to compared language complexity, efficiency, battery life comparison, etc.
