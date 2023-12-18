"""
File: main.py
Author: Zachary Milke
Description: Main module and controller for the Light Intensity System used to measure the
    amount of light present in an area and output relevant data to an OLED display. It uses two LDR
    sensors (for redundancy) and a 128 x 64 OLED display and is meant to run on a Raspberry Pi 
    Pico.

Created on: 10-DEC-2023
Updated on: 12-DEC-2023
"""


from machine import Pin, ADC
from dht import DHT11
from utime import sleep_ms
from sys import exit
from _thread import start_new_thread
from display import Display


def read_ldr_vals(sensor1: ADC, sensor2: ADC) -> list:
    """ Take a reading from each LDR and return a list of individual readings. 
        
    Params
    -----
    sensor1 [ADC, required] ADC pin the first LDR sensor is connected to.
    sensor2 [ADC, required] ADC pin the second LDR sensor is connected to.

    Returns
    -----
    A list of integer values taken from the LDR sensors.
    """

    return [sensor1.read_u16(), sensor2.read_u16()]


def calculate_delta(val1: int, val2: int) -> int:
    """ Calculate the difference between the provided LDR values. 
        
    Params
    -----
    val1 [int, required] LDR value taken from the first sensor.
    val2 [int, required] LDR value taken from the second sensor.

    Returns
    -----
    Integer calculated using the formula
        delta = |val1 - val2|
    """

    return abs(val1 - val2)


def calculate_percent_delta(val1: int, val2: int, avg_val: float, raw_delta: int) -> float:
    """ Calculate the percent difference between given values. This method is semi-optimized
    to only perform part of the procedure for finding percent delta as the other parts are taken
    care of elsewhere in the module. In its current state, it does not use the val1 nor val2 inputs
    so they could technically be removed, but leaving them in makes the code more readable so the
    decision was made to keep them.
    
    Params
    -----
    val1 [int, required] LDR value taken from the first sensor.
    val2 [int, required] LDR value taken from the second sensor.
    avg_val [float, required] Average of the two LDR values.
    raw_delta [int, required] Absolute value of the difference between the two values.

    Returns
    -----
    A float calculated using the percent difference formula
        % delta = (|v1 - v1| / [(v1 + v2) / 2]) * 100
    """

    return round(((raw_delta / avg_val) * 100.0), 2)


def calculate_average_val(val1: int, val2: int) -> float:
    """ Calculate the average value between the two LDR input values.

    Params
    -----
    val1 [int, required] LDR value taken from the first sensor.
    val2 [int, required] LDR value taken from the second sensor.

    Returns
    -----
    A float calculated by dividing the sum of the values by two.
    """

    return round((val1 + val2) / 2.0)


def print_data(val1: int, val2: int, raw_delta: int, perc_delta: float) -> None:
    """ Format and print the LDR values and delta to the console screen. 
    
    Params
    -----
    val1 [int, required] LDR value taken from the second sensor.
    val2 [int, required] LDR value taken from the second sensor.
    raw_delta [int, required] Difference between the LDR values.
    perc_delta [float, required] Difference between the LDR values as a percentage.
    
    Returns
    -----
    A formatted string containing LDR reading data.
    """

    print(f"LDR1 {val1}\tLDR2 {val2}\tDelta {raw_delta}\tPercentage Delta {perc_delta}")


def is_data_valid(perc_delta: float, max_perc_delta: float = 10.0) -> bool:
    """ Verifies that a set of LDR values are valid by checking that the percent delta between
    them is less than 10%.
    
    Params
    -----
    perc_delta [float, required] % delta value calculated from most recent data refresh.
    max_perc_delta [float, optional] Maximum allowed % delta. Values above this are invalid while
    those equal or less than are valid.

    Returns
    -----
    Boolean indicating whether the given perc_delta is valid or not.
    """

    return perc_delta <= max_perc_delta


class RunCoreFlag:
    """ This class holds the flag which indicates that a reading has taken place. """

    run_core = False

    @classmethod
    def set_run_flag(cls):
        """ Set the run core flag to True. """

        cls.run_core = True

    @classmethod
    def clear_run_flag(cls):
        """ Clear the run core flag by setting it to False. """

        cls.run_core = False

    @classmethod
    def get_run_flag(cls):
        """ Return the run core flag. """

        return cls.run_core


def core0_thread(reading_delay_ms: int, max_perc_delta: float, verbose_output: bool) -> None:
    """ Manages the data reading and processing. 
    
    Params
    -----
    reading_delay_ms [int, required] Duration of time in milliseconds between one reading
        of the LDR data and the next.
    max_perc_delta [float, required] Maximum allowed % delta.
    verbose_output [bool, required] Should output be printed to the console or not? Output
        is printed when True, otherwise no output will be printed.
    """

    try:
        # Setup the display, ADC pins needed to run the LDR sensors, and the DHT11 sensor.
        display = Display()
        ldr1, ldr2 = ADC(26), ADC(27)
        dht = DHT11(Pin(12))
    except ValueError:  # LDR was likely plugged into an invalid ADC pin.
        print("Unable to setup display/sensors.")

    # Loop until device loses power.
    while True:
        # Get the list of LDR and temperature/humidity readings from the sensors.
        val1, val2 = read_ldr_vals(ldr1, ldr2)
        dht.measure()
        temp, rel_hum = dht.temperature(), dht.humidity()

        # Temperature value needs to be converted to fahrenheit.
        temp_f = round((temp * 9.0 / 5.0) + 32.0, 2)

        # Calculate the average, raw delta, and percent delta values for the readings and check
        # the data's validity.
        avg_val = calculate_average_val(val1, val2)
        delta = calculate_delta(val1, val2)
        perc_delta = calculate_percent_delta(val1, val2, avg_val, delta)
        is_valid = is_data_valid(perc_delta, max_perc_delta)

        # Output data to the console if verbose output was requested.
        if verbose_output:
            print_data(val1, val2, delta, perc_delta)

        # Alert the second thread that the reading indicator needs to be lit. Then, update the
        # display and sleep until the next reading.
        RunCoreFlag.set_run_flag()
        display.update(val1, val2, avg_val, delta, perc_delta, is_valid, temp_f, rel_hum)
        sleep_ms(reading_delay_ms)


def core1_thread():
    """ Manages the indication that a reading has taken place by polling the RunCoreFlag. """

    global run_core
    global indicator_ontime_ms

    # Setup the LED used to indicate a reading has been taken. This program uses the onboard LED.
    reading_indicator = Pin(25, Pin.OUT)

    # RunCoreFlag may not be defined yet if this thread starts before data thread.
    # Try sleeping for 0.1s to see if it is, then try again.
    try:
        RunCoreFlag.get_run_flag()
    except NameError:
        sleep_ms(0.1)

    # Loop until device loses power.
    while True:
        # Wait for core 0 to signal start.
        while not RunCoreFlag.get_run_flag():
            pass

        # Light the indicator LED, sleep for the set delay and then shut it off.
        reading_indicator.on()
        sleep_ms(indicator_ontime_ms)
        reading_indicator.off()

        # Clear the run flag indicating this core has finished its task.
        RunCoreFlag.clear_run_flag()


def main():
    """ Main entrypoint of the file. """

    # Adjust the delay between readings and indicator LED ontime (both in ms). Don't go below 1000.
    reading_delay_ms = 15000

    global indicator_ontime_ms
    indicator_ontime_ms = 125

    # Set console output here. True = output, False = no output. Primarily used for debugging.
    console_output = False

    # Set the maximum allowed percentage delta for LDR values here.
    max_perc_delta = 25.0

    try:
        # Clear the run flag as a precaution.
        RunCoreFlag.clear_run_flag()

        # Create and start the reading indication thread, then start the data thread.
        second_thread = start_new_thread(core1_thread, ())
        core0_thread(reading_delay_ms, max_perc_delta, console_output)
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    main()
