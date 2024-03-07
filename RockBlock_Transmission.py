import serial
import time

class RockBlock:
    def __init__(self, serial_port):
        self.serial_port = serial_port
	
        self.serial = serial.Serial(serial_port, 19200, timeout=1)

    def send_message(self, message):
	    # Clear the buffer
	    self.serial.flushInput()
	    self.serial.flushOutput()

	    self.serial.write('AT+SBDD0\r')
	    print(self.serial.readline())
	    print("buffer cleared")
	    # Load message into the RockBlock buffer
	    self.serial.write('AT+SBDWT=' + message + '\r')
	    print(self.serial.readline()) # Read OK response
	    print("message loaded")

	    # Check status
	    self.serial.write('AT\r')
	    print(self.serial.readline())
	    print("\n")
	    
	    response = ''
	    # Initiate message transmission
	    self.serial.write('AT+SBDIX\r')
	    print("message sent")
	    response = self.serial.readline()
	    print(response)
	    status = "-1"
	    index = 0
	    while response.startswith('+SBDIX:') == False:
		response = self.serial.readline()
		print(str(index)+": "+response)
		if index >= 25:
			return -1
		index = index+1
	    print("response recieved: "+str(response))
	    
	    
	    
	    if response.startswith('+SBDIX:'):
		status = response.split(',')[0]
		
	    return int(status)

if __name__ == "__main__":
    rockblock = RockBlock('/dev/ttyUSB0')  # Update with your serial port
    sent = 0
    while sent == 0:
	message = "Hello, RockBlock!"
	success = rockblock.send_message(message)

	if success == 0:
		print("Message transmitted successfully!")
		sent = 1
	else:
		sent = 0
		print("Failed to transmit message. Status: "+str(success))
        
