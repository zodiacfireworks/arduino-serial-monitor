// Setup UV Sensor (ML8511) Pins
int UVOUT = A3;
int DELAY = 1000;

void setup() {
  Serial.begin(9600);

  pinMode(UVOUT, INPUT);
  analogReference(EXTERNAL);
}

void loop() {
  if (Serial.available() > 0) {
    DELAY = Serial.parseInt();
    
    Serial.print("M:");
    Serial.println(DELAY);
  }

  int uvLevel = averageAnalogRead(UVOUT);
  int refLevel = 1023;
  float outputVoltage = 3.3 / refLevel * uvLevel;
  // mW/cm^2
  float uvIntensity = mapfloat(outputVoltage, 0.99, 2.9, 0.0, 15.0);

  //Serial.print("MP8511 Output: ");
  //Serial.println(uvLevel);
  //Serial.print("MP8511 voltage: ");
  //Serial.println(outputVoltage);
  //Serial.print("UV Intensity (mW/cm^2): ");
  Serial.print("U:");
  Serial.println(uvIntensity<0?0:uvIntensity);
  
  delay(DELAY);

}

//Takes an average of readings on a given pin
//Returns the average
int averageAnalogRead(int pinToRead)
{
  byte numberOfReadings = 8;
  unsigned int runningValue = 0;

  for(int x = 0 ; x < numberOfReadings ; x++)
    runningValue += analogRead(pinToRead);
  runningValue /= numberOfReadings;

  return(runningValue);
}

//The Arduino Map function but for floats
//From: http://forum.arduino.cc/index.php?topic=3922.0
float mapfloat(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
