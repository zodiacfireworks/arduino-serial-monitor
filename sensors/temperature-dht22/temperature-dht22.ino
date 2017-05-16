#include <dht.h>

dht DHT;

#define DHT22_PIN 13

int DELAY=1000;

// dewPoint function NOAA
// reference (1) : http://wahiduddin.net/calc/density_algorithms.htm
// reference (2) : http://www.colorado.edu/geography/weather_station/Geog_site/about.htm
//

double dewPoint(double temperature, double humidity) {
  // (1) Saturation Vapor Pressure = ESGG(T)
  double RATIO = 373.15 / (273.15 + temperature);
  double RHS = -7.90298 * (RATIO - 1);
  RHS += 5.02808 * log10(RATIO);
  RHS += -1.3816e-7 * (pow(10, (11.344 * (1 - 1/RATIO ))) - 1) ;
  RHS += 8.1328e-3 * (pow(10, (-3.49149 * (RATIO - 1))) - 1) ;
  RHS += log10(1013.246);

  // factor -3 is to adjust units - Vapor Pressure SVP * humidity
  double VP = pow(10, RHS - 3) * humidity;

  // (2) DEWPOINT = F(Vapor Pressure)
  double T = log(VP/0.61078);   // temp var
  return (241.88 * T) / (17.558 - T);
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    DELAY = Serial.parseInt();
    
    Serial.print("M:");
    Serial.println(DELAY);
  }
  
  int chk = DHT.read22(DHT22_PIN);
  Serial.print("S:");
  Serial.print(chk);
  Serial.print("|T:");
  Serial.print(DHT.temperature, 2);
  Serial.print("|H:");
  Serial.print(DHT.humidity, 2);
  Serial.print("|W:");
  Serial.println(dewPoint(DHT.temperature,DHT.humidity), 2);
  delay(DELAY);
}

