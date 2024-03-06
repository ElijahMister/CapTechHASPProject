import smbus
import time

# Define the I2C address of the sensor
RAD_SENS_I2C_ADDR = 0x66

# Function to read a 16-bit unsigned integer from the sensor
def read_uint16(bus, register):
    data = bus.read_i2c_block_data(RAD_SENS_I2C_ADDR, register, 2)
    return (data[0] << 8) | data[1]

# Function to write a 16-bit unsigned integer to the sensor
def write_uint16(bus, register, value):
    bus.write_i2c_block_data(RAD_SENS_I2C_ADDR, register, [(value >> 8) & 0xFF, value & 0xFF])

# Create an instance of the smbus object
bus = smbus.SMBus(1)  # 1 indicates the I2C bus number

# Initialize the sensor
def init_sensor():
    # Check sensor wiring and initialize
    if not bus.read_byte(RAD_SENS_I2C_ADDR):
        print("Sensor wiring error!")
        return False
    return True

# Setup sensor sensitivity
def set_sensitivity(sensitivity):
    write_uint16(bus, 0x00, sensitivity)

# Setup HV generator state
def set_hv_generator_state(state):
    bus.write_byte(RAD_SENS_I2C_ADDR, 0x01 if state else 0x00)

# Setup LED indication state
def set_led_state(state):
    bus.write_byte(RAD_SENS_I2C_ADDR, 0x02 if state else 0x00)

# Main function
def main():
    if not init_sensor():
        return

    # Record the start time
    start_time = time.time()

    # Main loop 
    while True:
        # Calculate elapsed time
        elapsed_time = int(time.time() - start_time)

        # Read sensor data
        rad_intensity_dynamic = read_uint16(bus, 0x03)
        rad_intensity_static = read_uint16(bus, 0x04)
        num_pulses = read_uint16(bus, 0x05)

        # Print data along with elapsed time
        print(f"Time elapsed: {elapsed_time} seconds")
        print(f"Rad intensity dynamic: {rad_intensity_dynamic}")
        print(f"Rad intensity static: {rad_intensity_static}")
        print(f"Number of pulses: {num_pulses}")
        print()  # Add an empty line for better readability

        time.sleep(2)  # Delay for 2 seconds before reading again

if __name__ == "__main__":
    main()
