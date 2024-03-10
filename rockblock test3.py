import serial

class rockblock:
    __ser:serial.Serial
    
    def __init__(self, port:str):
        self.__ser = serial.Serial(port, 19200, timeout=1)

    def getLSB(self, binary:bin, nBits:int = 4): #returns a string of the lsb's for nBits   
        length = len(binary)
        lastBit = length - 1
        return_string = ""
        loop_Bits = nBits
        if(length-2 < nBits):
            loop_Bits = length-2
        for i in range(0,loop_Bits):
            return_string =  binary[lastBit-i]+return_string
        if(len(return_string) < nBits):
            while len(return_string) < nBits:
                return_string = "0" + return_string
        return return_string
        
    def closeSerialConnection(self): #just closes the serial connection, it does not clear the MO buffer
        self.__ser.close()
        
    def stopRF(self): #stops the RF signal *Untested*
        self.__ser.write("AT*Rn 0\r")
        self.wait_until_response()
        
    def startRF(self): #starts the RF signal *Untested*
        self.__ser.write("AT*Rn 1\r")
        self.wait_until_response()
        
    def getGPSPosition(self): #some rockblocks have gps functionality these functions are just in case we have one of those *Untested*
        self.__ser.write("+GPSPOS\r")
        self.wait_until_response()
    
    def enableGPS(self): #some rockblocks have gps functionality these functions are just in case we have one of those *Untested*
        self.__ser.write("+GPSSTA 1\r")
        self.wait_until_response()
        
    def wait_until_response(self): #keeps reading the input buffer until it gets a signal 
        x = 1
        while x == 1:
            y = ''
            y = self.__ser.readline()
            #print(str(y))
            if y.startswith("+SBDIX:") == True:
                x = 0
                return str(y)
            if y.startswith("+SBDS:") == True:
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

    def checkSum(self, string:str): #uses alternitive check sum
        sumation = 0
        #for each charactur in string add its ascii value together
        for c in string:
            sumation = sumation+ord(c)
        #take that value and convert it to binary
        s = bin(sumation)
        #find the 8 least significant bits
        x = self.getLSB(s,8)
        s = s.removesuffix(x)
        y = self.getLSB(s,8)
        x = int(x,2)
        y = int(y,2)
        print(chr(x)+chr(y))
        return(chr(x)+chr(y))
    
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




