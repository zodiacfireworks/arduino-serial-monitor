int DELAY=1000;

int rainPin  = A0;
int greenLED = 2;
int amberLED = 4;
int redLED   = 7;

int thresholdValueLower = 500;
int thresholdValueUpper = 800;

void setup(){
  pinMode(rainPin, INPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(amberLED, OUTPUT);
  
  pinMode(redLED, OUTPUT);
  digitalWrite(greenLED, LOW);
  digitalWrite(redLED, LOW);
  
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    DELAY = Serial.parseInt();
    
    Serial.print("M:");
    Serial.println(DELAY);
  }

  float soil_moisture = float(analogRead(rainPin));

  Serial.print("L:");
  Serial.println(soil_moisture, 2);
  
  if(soil_moisture < thresholdValueLower){
    // Serial.println(" - La humedad del suelo está en niveles optimos");
    digitalWrite(redLED, LOW);
    digitalWrite(amberLED, LOW);
    digitalWrite(greenLED, HIGH);
  }
  else if(thresholdValueLower < soil_moisture && soil_moisture < thresholdValueUpper){
    // Serial.println(" - La humedad del suelo está en niveles permisibles, considere activar el sistema de regadio");
    digitalWrite(redLED, LOW);
    digitalWrite(amberLED, HIGH);
    digitalWrite(greenLED, LOW);
  }
  else {
    // Serial.println(" - Los niveles de humedad estan por debajo de lo permitido, el sistema de regadio se activará automáticamente");
    digitalWrite(redLED, HIGH);
    digitalWrite(amberLED, LOW);
    digitalWrite(greenLED, LOW);
  }
  
  delay(DELAY);
}
