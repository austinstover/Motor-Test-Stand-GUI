/*
 * @author Austin Stover
 * October 2016
 * A helper program to send serial data
 * NOTE: Serial.begin() must be called before any of the send functions in this file
 */

long lastDeltaTime = 0;

void sendDebug(const char* message)
{
  int len = strlen(message);
  Serial.write(MAGIC_NUM); //Header: Magic number
  Serial.write(DEBUG_STRING); //Payload: key
  Serial.write(len >> 8); //Payload: Value: length of string
  Serial.write(len);
  byte dataOut[len + 2];
  dataOut[0] = len >> 8;
  dataOut[1] = len;
  for (int n = 0; n < len; n++)
  {
    Serial.write(message[n]); //Payload: Value: string
    dataOut[n + 2] = (byte)message[n];
  }
  Serial.write(lRCheck(dataOut, len + 2));
  Serial.flush();
}

void sendError(const char* message)
{
  int len = strlen(message);
  Serial.write(MAGIC_NUM);
  Serial.write(ERROR_STRING);
  Serial.write(len >> 8);
  Serial.write(len);
  byte dataOut[len + 2];
  dataOut[0] = len >> 8;
  dataOut[1] = len;
  for (int n = 0; n < len; n++)
  {
    Serial.write(message[n]); //Payload: Value: string
    dataOut[n + 2] = (byte)message[n];
  }
  Serial.write(lRCheck(dataOut, len + 2));
  Serial.flush();
}

void sendTimestamp(unsigned long timestamp)
{
  Serial.write(MAGIC_NUM);
  Serial.write(TIMESTAMP);
  byte dataOut[4] = {timestamp >> 24, timestamp >> 16, timestamp >> 8, timestamp};
  Serial.write(dataOut, 4);
  Serial.write(lRCheck(dataOut, 4));
  Serial.flush();
}

void sendPotentiometer(short reading)
{
  Serial.write(MAGIC_NUM);
  Serial.write(POTENTIOMETER);
  byte dataOut[2] = {reading >> 8, reading};
  Serial.write(dataOut, 2);
  Serial.write(lRCheck(dataOut, 2));
  Serial.flush();
}

void sendRawTemp(short reading)
{
  Serial.write(MAGIC_NUM);
  Serial.write(RAW_TEMP);
  byte dataOut[2] = {reading >> 8, reading};
  Serial.write(dataOut, 2);
  Serial.write(lRCheck(dataOut, 2));
  Serial.flush();
}

void sendConvertedTemp(float celsius)
{
  Serial.write(MAGIC_NUM);
  Serial.write(CONVERTED_TEMP);
  
  union data //Float conversion from Puneet Sashdeva
  {
    float a;
    byte datas[4];
  }
  data;

  data.a = celsius;
  Serial.write(data.datas[0]);
  Serial.write(data.datas[1]);
  Serial.write(data.datas[2]);
  Serial.write(data.datas[3]);
  Serial.write(lRCheck(data.datas, 4));
  Serial.flush();
}

/*
 * Sets a delta time loop for the communication--use this with an if() block
 * @param period The time in between runs in milliseconds
 * @return True if the period has passed
 */
bool newPeriod(long period)
{
  long deltaTime = millis() - lastDeltaTime;
  if (deltaTime > period)
  {
    lastDeltaTime = millis();
    return true;
  }
  return false;
}
