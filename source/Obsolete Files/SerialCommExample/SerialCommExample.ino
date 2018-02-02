/*
 * @author Austin Stover
 * July 2017
 * This program demonstrates transmission of data over a serial connection between an 
 * Arduino and a computer.
 */

const byte MAGIC_NUM = '!';

// Types of Messages:
const byte DEBUG_STRING = 0x30;
const byte ERROR_STRING = 0x31;
const byte TIMESTAMP = 0x32; //4-Byte Integer
const byte POTENTIOMETER = 0x33; //2-Byte Integer
const byte RAW_TEMP = 0x34; //2-Byte Integer
const byte CONVERTED_TEMP = 0x35; //4-Byte Float

int calcLRC; //Calculated Longitudinal Redundancy Check byte

const int DATA_STRING_SIZE = 51;
char dataString[DATA_STRING_SIZE] = ""; //A char array to hold each message's data--its length limits message size


void setup()
{
  Serial.begin(9600);
}

void loop()
{
//  if(newPeriod(500))
//  {
//    sendDebug("Hello World");
//    sendError("Help");
//    sendTimestamp(64);
//    sendPotentiometer(-17);
//    sendRawTemp(124);
//    sendConvertedTemp(1.23);
//  }


  if(Serial.available())
  {
    delay(1);
    if(Serial.read() == MAGIC_NUM)
    {
      delay(1);
      byte typeByte = Serial.read();
      int returnInt;
      memset(dataString, 0, DATA_STRING_SIZE * sizeof(char)); //Make char array empty by setting it to nulls
      returnInt = readData(typeByte, dataString, DATA_STRING_SIZE);
      delay(1);
      byte lRCIn = Serial.read();
      
      if(returnInt == 0 && calcLRC == lRCIn) //If no problems and no transcription errors
      {
        sendDebug(dataString);
      }
    }
  }
  
}

/**
 * Calculates the Longitudinal Redundancy Check byte
 * @param data The payload as an array of bytes
 * @param dataLength The length of data[]
 * @return The LRC byte
 */
byte lRCheck(byte data[], int dataLength)
{
  int lRC = 0;
  for(int i = 0; i < dataLength; i++)
  {
    lRC = (lRC + data[i]) & 0xFF;
  }
  lRC = ((lRC ^ 0xFF) + 2) & 0xFF;
  return (byte)lRC;
}
