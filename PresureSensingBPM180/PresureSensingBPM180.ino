#include <SFE_BMP180.h>
#include <Wire.h>

SFE_BMP180 bpm180;

int DELAY = 1000;

char status;
char error;
double T,P,p0,a;

void setup() {
  Serial.begin(9600);
  bpm180.begin();
}

void loop() {
  if (Serial.available() > 0) {
    DELAY = Serial.parseInt();
    
    Serial.print("M:");
    Serial.println(DELAY);
  }

  status = bpm180.startTemperature();
  if (status != 0) {
    delay(status);
    status = bpm180.getTemperature(T);
    
    if (status == 0) {
      T = -999.0;
    }
    
    status = bpm180.startPressure(3);
    if (status != 0) {
      delay(status);
        
      status = bpm180.getPressure(P,T);
      if (status == 0) {
        P = -999.0;
      }
      else {
        // P in atm
        // P = P*0.986923267;
        // P in mmHg
        P = P*0.750061561;
      }
    }
  }
   
  error = bpm180.getError();

  Serial.print("S:");
  Serial.print(int(error));
  Serial.print("|T:");
  Serial.print(T, 2);
  Serial.print("|P:");
  Serial.println(P, 2);
  delay(DELAY);
}
