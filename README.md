# Light Monitor

A Raspberry Pi Pico &amp; MicroPython driven system that measures the intensity of light using LDR sensors and an displays data OLED display.

![License](https://img.shields.io/badge/License-GPL3.0-blue)

A small project used to measure the intensity of light using a Raspberry Pi Pico and two adjustable LDRs written in MicroPython. The system uses two LDR sensors for redundancy and displays relevant information on a small oled screen.

It can be powered via a micro-usb cable and 5v power supply or via rechargeable lithium ion battery.

## Installation and Use

All that is needed to "install" is to copy the main.py and LIS_display.py files onto the Pico device. This can be done any number of ways, but I used the Thonny editor when designing and testing which made things easy as files can be saved directly to the device memory through it.

To use the system all you need to do is power the Pico device on. As the controller file is named main.py, it should start automatically. To avoid it from running at power on, rename the file to something else, e.g., LIS_driver.py.

## Future

Once the system is stable, it would be cool to rewrite the entire thing in C using the Pico SDK. Could be used to compared language complexity, efficiency, battery life comparison, etc.
