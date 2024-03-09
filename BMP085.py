# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 14:01:19 2024

@author: owen_
"""

import smbus
import time

# Define BMP085 constants
BMP085_I2C_ADDRESS = 0x77
BMP085_REG_CONTROL = 0xF4
BMP085_REG_TEMP = 0xF6
BMP085_REG_PRESSURE = 0xF6
BMP085_COMMAND_TEMPERATURE = 0x2E
BMP085_COMMAND_PRESSURE = 0x34

# Open I2C bus
bus = smbus.SMBus(1)  # Change to 0 for older Raspberry Pi boards

# Read temperature from BMP085
def read_temperature():
    bus.write_byte_data(BMP085_I2C_ADDRESS, BMP085_REG_CONTROL, BMP085_COMMAND_TEMPERATURE)
    time.sleep(0.005)  # Wait for temperature conversion
    raw_temp = bus.read_word_data(BMP085_I2C_ADDRESS, BMP085_REG_TEMP)
    raw_temp = ((raw_temp << 8) & 0xFF00) + (raw_temp >> 8)
    temp = ((raw_temp - 0x0000) * 0.1)  # Celsius
    return temp

# Read pressure from BMP085
def read_pressure():
    bus.write_byte_data(BMP085_I2C_ADDRESS, BMP085_REG_CONTROL, BMP085_COMMAND_PRESSURE + (3 << 6))
    time.sleep(0.014)  # Wait for pressure conversion
    msb = bus.read_byte_data(BMP085_I2C_ADDRESS, BMP085_REG_PRESSURE)
    lsb = bus.read_byte_data(BMP085_I2C_ADDRESS, BMP085_REG_PRESSURE + 1)
    xlsb = bus.read_byte_data(BMP085_I2C_ADDRESS, BMP085_REG_PRESSURE + 2)
    pressure_raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - 3)
    pressure = (pressure_raw * (101.325 / 65536.0))  # kPa
    return pressure

# Main function
def main():
    try:
        while True:
            temperature = read_temperature()
            pressure = read_pressure()
            print("Temperature: {:.2f} °C".format(temperature))
            print("Pressure: {:.2f} kPa".format(pressure))
            time.sleep(1)  # Wait for 1 second before the next reading

    except KeyboardInterrupt:
        print("Measurement stopped by the user")

if __name__ == "__main__":
    main()
