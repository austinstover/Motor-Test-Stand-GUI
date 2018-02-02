'''
@author Austin Stover
July 2017
This program demonstrates transmission and reception of serial data sent with SerialComm.ino

Protocol
Byte number:        1.                2.                   3.              4.                           N.
Description: [ Magic Number ][ Type Identifier Key ][ Data Payload ][ Data Payload ] etc... [ Error Check (LRC) Byte ]
'''

import serial
import struct

MAGIC_NUM = ord('!')
DEBUG_STRING = 0x30                 #UTF encoded string
ERROR_STRING = 0x31                 #UTF encoded string
TIMESTAMP = 0x32                    #4-Byte Integer
POTENTIOMETER = 0x33                #2-Byte Integer
RAW_TEMP = 0x34                     #2-Byte Integer
CONVERTED_TEMP = 0x35               #4-Byte Float

calcLRC = b''                       #Calculated error check byte (Volatile Global Var)
ser = serial.Serial('COM6', 9600)   #Define a pySerial object


def main():
    while True:
        if(ser.in_waiting > 1000):                          #If too many bytes fill buffer, clear it
            ser.reset_input_buffer();
        elif(ser.in_waiting > 0):                           #If bytes are available in buffer
            if(ser.read()[0] == MAGIC_NUM):                 #If 1st byte = magic number
                typeByte = ser.read()[0]                    #Read the type identifier byte
                dataString = readData(typeByte)
                lRCIn = ser.read()                          #Read error check byte
                if(dataString != "" and calcLRC == lRCIn):  #Ensure type byte found and do error check
                    print(dataString)

        sendDebug("Hello World!")
        sendError("Help!")
        sendTimestamp(64)
        sendPotentiometer(-17)
        sendRawTemp(124)
        sendConvertedTemp(3.14159265)

        
# Input Functions:

'''
Return the payload following the type identifier key
@param typeOfDataByte The type identifier key integer specifying the payload
@return The payload, or an empty string if the key was not recognized
'''
def readData(typeOfDataByte):
    if(typeOfDataByte == DEBUG_STRING):
        print("Debug: ", end="")
        return readUTF()
    elif(typeOfDataByte == ERROR_STRING):
        print("Error: ", end="")
        return "!!! " + readUTF()
    elif(typeOfDataByte == TIMESTAMP):
        print("Timestamp: ", end="")
        return readInt()
    elif(typeOfDataByte == POTENTIOMETER):
        print("Potentiometer: ", end="")
        return readShort()
    elif(typeOfDataByte == RAW_TEMP):
        print("Raw Temp: ", end="")
        return readShort()
    elif(typeOfDataByte == CONVERTED_TEMP):
        print("Converted Temp: ", end="")
        return readFloat()
    else:
        return ""

'''Reads a string in UTF format (An Arduino C String)'''
def readUTF():
    dataIn = ser.read(size=2)
    lenStr = struct.unpack('>H', dataIn)[0] #First 2 bytes (unsigned short) define length of string
    message = '';
    for i in range(lenStr):                 #Remaining bytes define string
        datumIn = ser.read()
        dataIn += datumIn
        message += chr(datumIn[0])
    global calcLRC
    calcLRC = lRCheck(dataIn)
    return message

'''Reads a signed 4-Byte integer (An Arduino C long) in big-endian format'''
def readInt():
    dataIn = ser.read(size=4)
    global calcLRC
    calcLRC = lRCheck(dataIn)
    return struct.unpack('>i', dataIn)[0]

'''Reads a signed 2-Byte integer (An Arduino C int) in big-endian format'''
def readShort():
    dataIn = ser.read(size=2)
    global calcLRC
    calcLRC = lRCheck(dataIn)
    return struct.unpack('>h', dataIn)[0]

'''Reads a 4-Byte float (An Arduino C double/float) in little-endian format'''
def readFloat():
    dataIn = ser.read(size=4)
    global calcLRC
    calcLRC = lRCheck(dataIn)
    return struct.unpack('<f', dataIn)[0]


#   Output Functions:

def sendDebug(stringToSend):
    ser.write(bytes([MAGIC_NUM]))
    ser.write(bytes([DEBUG_STRING]))
    dataOut = struct.pack('>H', len(stringToSend))
    dataOut += bytes(stringToSend, 'UTF-8')
    ser.write(dataOut)
    ser.write(lRCheck(dataOut))
    ser.flush()

def sendError(stringToSend):
    ser.write(bytes([MAGIC_NUM]))
    ser.write(bytes([ERROR_STRING]))
    dataOut = struct.pack('>H', len(stringToSend))
    dataOut += bytes(stringToSend, 'UTF-8')
    ser.write(dataOut)
    ser.write(lRCheck(dataOut))
    ser.flush()

def sendTimestamp(intToSend):
    ser.write(bytes([MAGIC_NUM]))
    ser.write(bytes([TIMESTAMP]))
    dataOut = struct.pack('>i', intToSend)
    ser.write(dataOut)
    ser.write(lRCheck(dataOut))
    ser.flush()

def sendPotentiometer(shortToSend):
    ser.write(bytes([MAGIC_NUM]))
    ser.write(bytes([POTENTIOMETER]))
    dataOut = struct.pack('>h', shortToSend)
    ser.write(dataOut)
    ser.write(lRCheck(dataOut))
    ser.flush()

def sendRawTemp(shortToSend):
    ser.write(bytes([MAGIC_NUM]))
    ser.write(bytes([RAW_TEMP]))
    dataOut = struct.pack('>h', shortToSend)
    ser.write(dataOut)
    ser.write(lRCheck(dataOut))
    ser.flush()

def sendConvertedTemp(floatToSend):
    ser.write(bytes([MAGIC_NUM]))
    ser.write(bytes([CONVERTED_TEMP]))
    dataOut = struct.pack('<f', floatToSend)
    ser.write(dataOut)
    ser.write(lRCheck(dataOut))
    ser.flush()


# Error Check Function

'''
Calculates the longitudinal redundancy check byte
@param data The payload
@return The LRC byte (A Bytes object)
'''
def lRCheck(dataIn):
    lRC = 0
    for b in dataIn:
        lRC = (lRC + b) & 0xFF
    lRC = ((lRC ^ 0xFF) + 2) & 0xFF
    return bytes([lRC])

if __name__ == '__main__':
    main()

