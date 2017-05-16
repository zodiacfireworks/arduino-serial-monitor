const int xPin = 0;
const int yPin = 1;
const int zPin = 2;

int minVal = 265;
int maxVal = 402;

double x;
double y;
double z;

#define PI 3.14159265
#define RAD_TO_DEG 57.2957786

int DELAY = 100;

void setup(){
  Serial.begin(9600); 
}


void loop(){
  if (Serial.available() > 0) {
    DELAY = Serial.parseInt();
    
    Serial.print("M:");
    Serial.println(DELAY);
  }
  
  int xRead = analogRead(xPin);
  int yRead = analogRead(yPin);
  int zRead = analogRead(zPin);

  //Serial.print("X:");
  //Serial.print(xRead);
  //Serial.print("|Y:");
  //Serial.print(yRead);
  //Serial.print("|Z:");
  //Serial.println(zRead);
  
  int xAng = map(xRead, minVal, maxVal, -90, 90);
  int yAng = map(yRead, minVal, maxVal, -90, 90);
  int zAng = map(zRead, minVal, maxVal, -90, 90);

  x = RAD_TO_DEG * (atan2(-yAng, -zAng) + PI);
  y = RAD_TO_DEG * (atan2(-xAng, -zAng) + PI);
  z = RAD_TO_DEG * (atan2(-yAng, -xAng) + PI);

  Serial.print("X:");
  Serial.print(x);
  Serial.print("|Y:");
  Serial.print(y);
  Serial.print("|Z:");
  Serial.println(z);
  delay(DELAY);
}
