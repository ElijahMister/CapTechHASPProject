# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
    
import time
import serial
import csv
import os

    
#DEBUG 

DEBUG_OUTPUT = False

demo_uplink = chr(1)+chr(2)+chr(5)+'P'+chr(3)+chr(13)+chr(10)
demo_uplink_2 = chr(1)+chr(2)+chr(53)+'c'+chr(3)+chr(13)+chr(10)
demo_uplink_3 = chr(5)+chr(1)+chr(2)+chr(53)+'c'+chr(3)+chr(13)+chr(10)
demo_uplink_4 = 'x34'
demo_uplink_5 = 'x34543454'
demo_uplink_6 = ''
demo_uplink_7 = chr(1)+chr(2)+chr(53)+'a'+chr(3)+chr(13)+chr(10)

#END DEBUG
class TELEMETRY_CODES:
    NULL = 0
    STATUS = 1
    DATA = 2
    TARGET = 3
    ERROR = 4
    COMMAND = 5


class payload_data:
    __temp_1 = 0;
    __temp_2 = 0;
    __temp_3 = 0;
    __temp_4 = 0;
    __altitude = 0;
    __pressure = 0;
    __time_stamp = 0;
    __trapsat_door = 0;
    
    __file_index = 0;
    __file_name = "SaveFile";
    __csv_file = None;
    __csv_writer = None;
    __line_index = 0;
    
    def __init__(self, file_name:str = "TRAPSat_Data_"):
        self.__file_name = file_name
        self.__csv_file = open(self.__file_name+str(self.__file_index), 'w')
            
    def writeDataToFile(self):
        self.__csv_writer = csv.writer(self.__csv_file)
        self.__csv_writer.writerow([self.__line_index, time.time(), self.__trapsat_door, self.__temp_1, self.__temp_2, self.__temp_3, self.__temp_4])
        self.__line_index = self.__line_index+1
        
    def closeFile(self):
        self.__csv_file.close()
            
    def closeAndStartNewFile(self):
        self.__csv_file.close()
        self.__line_index = 0
        self.__file_index = self.__file_index+1 
        self.__csv_file = open(self.__file_name+str(self.__file_index), 'w')
        
    def getLineIndex(self):
        return self.__line_index
    
    def getFileIndex(self):
        return self.__file_index
    
    def getFileIndexAsString(self):
        return str(self.__file_index)

    def getLastFile(self):
        #Finds the last saved file.
        folder_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the Python script

        # List all files in the directory
        files = os.listdir(folder_path)

        # Filter files based on the naming pattern
        relevant_files = [file for file in files if file.startswith("TRAPSat_Data_")]

        if not relevant_files:
            print("No relevant files found.")
            return 0

        # Extract sequence numbers and find the maximum
        sequence_numbers = [int(file.split("_")[-1]) for file in relevant_files]
        max_sequence_number = max(sequence_numbers)

        return max_sequence_number
    
    def setFileIndex(self, newIndex):
        #Sets a new file index. Opens a folder that starts at that index.
        self.__file_index = newIndex
        self.__csv_file = open(self.__file_name+str(self.__file_index), 'w')
    
class systems_status:
    __telemetry = 1;
    __rockblock = 1;
    __camera = 1;
    __temp_1 = 1;
    __temp_2 = 1;
    __temp_3 = 1;
    __temp_4 = 1;
    __altitude = 1;
    
    class ERROR_CODES:
        OK = 0;
        DID_NOT_INITIALIZE_SERIAL = 1
        DID_NOT_RESPOND = 2
        SUSPICOUS_DATA_RESPONSE = 3
        I2C_ERROR = 4
        UNEXPECTED = 5
        
    def __init__(self):
        pass
    
    def setRockblockStatus(self, status = False):
        self.__rockblock = status;
        
    def setTelemetryStatus(self, status = False):
        self.__telemetry = status;
        
    def setCameraStatus(self, status = False):
        self.__camera = status;

    def getRockblockStatus(self):
        return self.__rockblock;
    
    def getTelemetryStatus(self):
        return self.__telemetry
    
    def getCameraStatus(self):
        return self.__camera;
    
class timer:
    __target_time = 0;
    __start_time = 0;
    __target = 0;
    __id = 0;
    
    def __init__(self, target:float = 600):
        self.__target = target
        self.__start_time = time.time()
        self.__target_time = self.__start_time+target
        self.__id = id(self)
    
    def update(self):
        if(time.time() >= self.__target_time):
            return True
        else:
            return False
        
    def countDown(self):
        print(str(self.__target_time - time.time()))
        
    def getTargetAsString(self):
        return str(self.__target);
        
    def resetTimer(self, target = -1):
        if(target > 0):
            self.__target = target
        self.__start_time = time.time()
        self.__target_time = self.__start_time+self.__target
    
    

def TRAPSat_open():
    door_status = 1;
    serialTelemetry(TELEMETRY_CODES.STATUS, "TRAPSAT OPEN")
    return

def TRAPSat_close():
    door_status = 0;
    serialTelemetry(TELEMETRY_CODES.STATUS, "TRAPSAT CLOSED")
    return
    
def serialTelemetry(code, data:str = ""):

    # Record type + TImestamp+NanoSeconds+Record Size+LS 8 bits+ Data
    #this will add to the telemetry when the trapsat door
    #status has changed
    t = time.time()
    time_stamp = int(t)
    time_stamp_ns = int((t-int(t))*10000)
    downlink = str(code)+" "+str(time_stamp)+" "+str(time_stamp_ns)+" "+str(data)+"\n"
    print(downlink,end = "")


def serialValidateCommand(data:str):
    cmd = "0"; # Empty command, do not use for anything else
    error = 0;      # used to log the error type
    
    if len(data) != 2:
        error = 1;
        
    #Get our command in binary
    cmd_bin = bin(ord(data[1]))
    # Get our commands lsb
    
    y = cmd_bin[5]+cmd_bin[6]+cmd_bin[7]+cmd_bin[8]
    
    # Use this to construct what what we should get for our check sum
    checksum_predicted = y+"0101"
    #print(checksum)
    
    #get our check sum and remove the 0b in front
    checksum_actual = bin(ord(data[0]))
    checksum_actual = checksum_actual.removeprefix("0b")
    
    
    #make sure it has any leading zeros it might have lost
    if len(checksum_actual) < 8:
        while 8-len(checksum_actual) != 0:
            checksum_actual = "0"+checksum_actual
        
    if DEBUG_OUTPUT == True:
        print("Commanding Validation:")
        print("\tPredicted: "+str(checksum_predicted))
        print("\tExpected: "+str(checksum_actual))
    #Check to make sure the two are equal
    if checksum_actual == checksum_predicted:
        if DEBUG_OUTPUT == True:
            print("\tCommand Valid")
        cmd = data[1]
        serialTelemetry(TELEMETRY_CODES.COMMAND, "Command Validated: Command: "+str(cmd))
    else:
        if DEBUG_OUTPUT == True:
            print("\tCommand Invalid")
        error=1;
        cmd = "ERROR"
    
    if error != 0:
        serialTelemetry(TELEMETRY_CODES.ERROR, "Invalid command: Error #"+str(error))
    
    return cmd;
    

def serialCommanding(data:str):
    error_code = 0;
    #
    #GET DATA FROM THE SERIAL HERE
    #
        
    #Data will be sent with a bunch of extra data we need to remove
    if len(data) != 7:
        error_code = 1;

    cmd = data.removeprefix(chr(1)+chr(2))
    cmd = cmd.removesuffix(chr(3)+chr(13)+chr(10))
    if len(cmd) != 2:
        error_code = 2;
    if error_code == 0:
        cmd = serialValidateCommand(cmd);
    else:
        cmd = "ERROR_STRING"
    
    if cmd == "0":
        print ("NULL COMMAND RECIEVED")
    
    elif cmd == "s":
        #Start Experiments
        pass
        
    elif cmd == "R":
        #reset everything
        pass
    elif cmd == "N":
        #Nuke it and restart the pi
        restartPi()
        
    elif cmd == "r":
        #Stop Rockblock communications
        pass
    elif cmd == "o":
        #Open TRAPSat Door
        TRAPSat_open()
        
    elif cmd == "c":
        #Close TRAPSat Door
        TRAPSat_close()
        
    elif cmd == "P":
        #Ping, logs the ping in the telemetry
        serialTelemetry(TELEMETRY_CODES.STATUS, "PING")
        pass
    
    elif cmd == "B":
        #Rockblock Ping, attempts to send a ping 
        #using the rockblock communications
        pass
    
    else:
        #print ("UNRECOGNIZED COMMAND RECIEVED")
        serialTelemetry(TELEMETRY_CODES.ERROR, "UNRECOGNIZED COMMAND RECIEVED "+str(error_code))
        #Anyother command that got through validataion should be loged in the 
        #telemetry but not exicuted

def misoGetInfo(): #Gets info from the other pi
    pass

def misoSendInfo(): #sends info to the other pi
    pass

def i2cGetTemps():
    pass

def getAltitude():
    pass

def getPressure():
    pass

def i2cGetGiger():
    pass

def rockblockTest(ser:serial.Serial):
    #+SBDSX
    ser.write("RT")
    ser.readlines(1)
    #command = "AT+CGMM"
    #command = "AT+SBDSX\r"
    pass

def rockblockSendSMS(ser, data:str =""):
    #+SBDIX\r
    #+SBDWT\r
    #+SBDWB\r
    
    pass

def rockblockReadSMS(ser, data:str =""):
    #+SBRT\r
    #+SBRB\r
    command = "AT+SBRT\r"
    pass

def rockblockEndComs():
    ## from the document it looks like command (5.23) AT*Rn is what we need to use
    pass

def checkSaveShort():
    pass

def saveTextFile(file_number:int, data):
    try:
        f = open("data_text_" + str(file_number),"w")
        f.write(data)
        f.close()
        serialTelemetry(TELEMETRY_CODES.DATA, "FILE SAVED "+str(file_number))
    except:
        serialTelemetry(TELEMETRY_CODES.ERROR, "FILE SAVE ERROR")
        
def saveImageFile(file_number:str, data):
    pass

def restartPi():
    #Send some way to reboot the other pi
    os.system("reboot")

#this will let us track our system status
sys = systems_status()

#trys to activate the serial devices
try:
    ser_telm = serial.Serial('/dev/ttyS0', 1600)        #HASP Commanding 
    sys.setTelemetryStatus(systems_status.ERROR_CODES.OK)
except:
    sys.setTelemetryStatus(systems_status.ERROR_CODES.DID_NOT_INITIALIZE_SERIAL)
try:
    ser_cams = serial.Serial('/dev/ttyACM0', 1900)     #Serial Camera
    sys.setCameraStatus(systems_status.ERROR_CODES.OK)
except:
    sys.setCameraStatus(systems_status.ERROR_CODES.DID_NOT_INITIALIZE_SERIAL)
    pass
try:    
    ser_rock = serial.Serial('/dev/ttyUSB0', 19200)              #Rockblock communications
    sys.setRockblockStatus(systems_status.ERROR_CODES.OK)
except:
    sys.setRockblockStatus(systems_status.ERROR_CODES.DID_NOT_INITIALIZE_SERIAL)


def main():
    continue_loop = 1;
    serialTelemetry(TELEMETRY_CODES.STATUS, "READY")
    t = timer(2)
    x = payload_data()

    #Sets the file index if needed.
    if(x.getLastFile() != 0):
        x.setFileIndex(x.getLastFile() + 1)
    
    while continue_loop == 1:
        
        if(t.update() == True):
            t.resetTimer(2)
            x.writeDataToFile()
            serialTelemetry(TELEMETRY_CODES.TARGET, "TIMER "+t.getTargetAsString())
            
            if(x.getLineIndex() >= 10):
                x.closeAndStartNewFile()
                serialTelemetry(TELEMETRY_CODES.DATA, "DATAFILE SAVED AND OPENED "+x.getFileIndexAsString())
                

if __name__ == "__main__":
    main()
