import serial

class rockblock:
    __ser:serial.Serial
    
    def __init__(self, port:str):
        self.__ser = serial.Serial(port, 19200, timeout=1)
        
    def closeSerialConnection(self):
        self.__ser.close()
        
    def stopRF(self):
        self.__ser.write("AT*Rn 0\r")
        self.wait_until_response()
        
    def startRF(self):
        self.__ser.write("AT*Rn 1\r")
        self.wait_until_response()
        
    def getGPSPosition(self):
        self.__ser.write("+GPSPOS\r")
        self.wait_until_response()
    
    def enableGPS(self):
        self.__ser.write("+GPSSTA 1\r")
        self.wait_until_response()
    def wait_until_response(self):
        x = 1
        while x == 1:
            y = ''
            y = self.__ser.readline()
            #print(str(y))
            if y.startswith("+SBDIX:") == True:
                x = 0
                return str(y)
            if y == "OK\r\n" or y == "ERROR\r\n":
                x = 0
                return str(y)
            return(y)
    
    def test_response(self): #sends AT command, returns true if it gets the OK command
        self.__ser.write("AT\r")
        y = self.wait_until_response()
        return self.is_ok(y)
        
    def is_ok(message:str): # if message is OK returns true, otherwise returns false
        if message == "OK":
            return True
        else:
            return False
        
    def sendTextMessage(self, message, retry:int = 3): #attempt to send a message will try for retry times
        self.__ser.write('AT+SBDWT=' + message + '\r')
        response = self.wait_until_response()
        if response == "OK":
            for i in range(0, retry):
                print("retry: "+i)
                self.__ser.write('AT+SBDIX\r')
                response = self.wait_until_response()
                if response.startswith("+SBDIX:"):
                    response_array = self.parseSDIX(response)
                    if response_array[0] == 0 or response_array[0] == 1 or response_array[0] == 2: 
                        return True
        return False
                
        
    def getTextMessage(self): #get the message in the MT buffer
        self.__ser.write('AT+SBDRT\r')
        response = self.wait_until_response()
        if(response.startswith("+SBDRT")):
            response = response.removeprefix("+SBDRT: ")
        
        
    def updateAndCheckMailbox(self): #Contats the satalite sending a blank MO message
        self.clearBuffer()
        self.__ser.write("AT+SBDIX\r")
        response = self.wait_until_response()
        array = self.parseSDIX(response)
        return array[2]
        
    def checkMailbox(self): #checks the buffer to see if there is a new message, does not contact the satilite
        self.clearBuffer()
        self.__ser.write('AT+SBDS\r')
        response = self.wait_until_response()
        array = self.parseSBDSresponse(response)
        return array[2]
        
    def parseSDIX(string:str): #returns an array of the status messages from the SBDIX call
        SBDIX_array = []
        if(string.startswith("SBDIX:")):
            string = string.removeprefix("SBDIX: ")
            SBDIX_array = string.split(",")
            print(SBDIX_array)
            print(len(SBDIX_array))
            if len(SBDIX_array) != 6:
                return 1
            else: return SBDIX_array
        else:
            return 0
    
    def parseSBDS(string:str): #returns an array of the status messages from the SBDS call
        SBDIX_array = []
        if(string.startswith("SBDS:")):
            string = string.removeprefix("SBDIX: ")
            SBDS_array = string.split(",")
            print(SBDIX_array)
            print(len(SBDIX_array))
            if len(SBDIX_array) != 4:
                return 1
            else: return SBDS_array
        else:
            return 0
        
    def lengthCheck(string): #checks to make sure the message is below the limit of charactures
        if len(string) < 340:
            return True
        else: return False
    
    def packBytes(string):
        pass
    
    def unpackBytes(string):
        pass
    
    def clearBuffer(self): #clears the MO buffer
        self.__ser.write('AT+SBDD0\r')
        print(self.wait_until_response())
            
    def encode_textMessage(self, message:str): # encodes a message for transmission
        message_length = len(message)
        x = message_length.to_bytes(2, 'big')
        y = self.checkSum(message)
        return x + message.encode() + y
    
    def checkSum(self, string:str): #a checksum
        #THis checksum takes the last characture and the middle characture, rounded down and subtracts them
        #It then takes the first and second characture and finds the diffrence, rounded down
        #Use this for now but I found a better way to do it by adding all the charactures and finding the lsb
        #I just have to figure out how to do it.
        length = len(string)
        if length >= 2:
            midpoint = int(length/2)
            x = ord(string[len(string)-1])
            y = ord(string[len(string)-midpoint])
            a = ord(string[0])
            b = ord(string[1])
            z = abs(x-y)
            c = abs(a-b)
        else:
            z = ord(string[0])
            c = ord(string[0])
        return z.to_bytes(1, 'big') + c.to_bytes(1, 'big')
    
    def decode_textMessage(self, message:str):
        #Dose the oppisie of encode and validates the data sent
        message_length = message[0] + message[1]
        m = self.splitString(message.decode(), 2, message_length)
        c = self.checkSum(m)
        r = int(message_length).to_bytes(2, 'big')+m.encode()+c
        if(r == message):
            return m
        else: return "ERROR-LEN"
    
    def splitString(string:str, start:int, end:int): #splits a string from start charactures to end charactures
        rString = ""
        for i in range(start, end+2):
            rString = rString+string[i]
        return rString
    

    
# print("1")


# #serial.flushInput()
# #serial.flushOutupt()

# ser.flushInput()
# ser.flushOutput()
# rockblock_clearBuffer(ser)

# #print("AT")
# rockblock_test(ser)
# print('3')
# message="XXXX"
# rockblock_sendMessage(ser, message)
# ser.close()




