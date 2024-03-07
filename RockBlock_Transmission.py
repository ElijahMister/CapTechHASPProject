import serial
import time

class RockBlock:
    def __init__(self, serial_port):
        self.serial_port = serial_port
        self.serial = serial.Serial(serial_port, 19200, timeout=1)

    def send_message(self, message, max_attempts=4):
        for attempt in range(max_attempts):
            # Clear the buffer
            self.serial.flushInput()
            self.serial.flushOutput()

            # Load message into the RockBlock buffer
            self.serial.write(b'AT+SBDWT=' + message.encode() + b'\r\n')
            self.serial.readline()  # Read OK response

            # Initiate message transmission
            self.serial.write(b'AT+SBDIX\r\n')
            response = self.serial.readline().decode().strip()

            if response.startswith('+SBDIX:'):
                status = response.split(',')[1]
                if int(status) == 0:
                    return True  # Transmission successful
            time.sleep(2)  # Wait before next attempt
        return False  # All attempts failed

if __name__ == "__main__":
    rockblock = RockBlock('/dev/ttyUSB0')  # Update with your serial port

    message = "Hello, RockBlock!"
    success = rockblock.send_message(message)

    if success:
        print("Message transmitted successfully!")
    else:
        print("Failed to transmit message after 4 attempts.")
