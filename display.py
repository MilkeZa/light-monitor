"""
File: display.py
Author: Zachary Milke
Description: This file manages the creation of and updating of the display and output text shown
    on the SSD1306 OLED display. It accepts data from the main module and displays it on screen.

Created on: 11-DEC-2023
Updated on: 15-DEC-2023
"""


from machine import Pin, I2C
from ssd1306 import SSD1306_I2C


class Display:
    """ A class to manage the output of data from the main module. """

    def __init__(self):
        # Setup the oled display
        self.display = None
        _sda_pin = Pin(14, Pin.OUT)
        _scl_pin = Pin(15, Pin.OUT)
        _i2c = I2C(1, sda=_sda_pin, scl=_scl_pin, freq=100000)
        self.display = SSD1306_I2C(128, 64, _i2c)

        # Initialize display text values and update the display.
        self.val1_base_text         = "S1 = "
        self.val2_base_text         = "S2 = "
        self.avg_base_text          = "Avg. = "
        self.raw_delta_base_text    = "R delta = "
        self.perc_delta_base_text   = "% delta = "
        self.is_valid_base_text     = "Valid = "
        self.temp_base_text         = "Temp. F = "
        self.humidity_base_text     = "Humidity = "

        # Update the text shown on the screen.
        self.update()

    def update(self, val1: int = -1, val2: int  = -1, avg: float  = -1.0,
                       raw_delta: int = -1, perc_delta: float = -1.0,
                       is_valid: bool = False,
                       temp_f: float = -1.0, rel_hum: float = -1.0) -> None:
        """ Refreshes the display, setting the available text. 
        
        Params
        -----
        val1 [int, optional] LDR value taken from the first sensor.
        val2 [int, optional] LDR value taken from the second sensor.
        avg [float, optional] Average of the two LDR values.
        raw_delta [int, optional] Absolute value of the difference between the two values.
        perc_delta [float, optional] Difference between the LDR values as a percentage.
        is_valid [bool, optional] Indicates whether the perc_delta is within an acceptable range.
        temp_f [float, optional] Temperature in degrees fahrenheit.
        rel_hum [float, optional] Relative humidity as a percentage out of 100.
        """

        # Fill the screen with black pixels and set the display text. Lastly, call the show method.
        self.display.fill(0)

        self.display.text(f"{self.val1_base_text}{val1}", 0, 0)
        self.display.text(f"{self.val2_base_text}{val2}", 0, 8)
        self.display.text(f"{self.avg_base_text}{avg}", 0, 16)
        self.display.text(f"{self.raw_delta_base_text}{raw_delta}", 0, 24)
        self.display.text(f"{self.perc_delta_base_text}{perc_delta}", 0, 32)
        self.display.text(f"{self.is_valid_base_text}{is_valid}", 0, 40)
        self.display.text(f"{self.temp_base_text}{temp_f}", 0, 48)
        self.display.text(f"{self.humidity_base_text}{rel_hum}%", 0, 56)

        self.display.show()


def main():
    """ Main entrypoint of the file. """

    # Create a test display and attempt to update it with fake data.
    display = Display()
    display.update(00000, 00000, 0.0, 0, 0.0, False, 0.0, 0.0)


if __name__ == "__main__":
    main()
