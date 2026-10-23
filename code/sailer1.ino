const int PIN_FURL = 9;
const int PIN_SHEET = 6;
const int PIN_RUDDER = 5;
const int PIN_WINDDIR = 14; // A0
const int PIN_WINDSPD = 2;
volatile int windspeed_counter = 0;
unsigned long previousMillis = 0;
const long wspd_interval = 1000; // 1 second
float frequency = 0;
float wspd_mph;
uint8_t rudder_angle = 0;
uint8_t sheet_angle = 0;

void setup()
{
  pinMode(PIN_SHEET, OUTPUT);
  pinMode(PIN_RUDDER, OUTPUT);
  pinMode(PIN_FURL, OUTPUT);
  pinMode(PIN_WINDDIR, INPUT);
  
  pinMode(PIN_WINDSPD, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_WINDSPD), windspdInterrupt, FALLING);
  
  Serial.begin(9600); // Initialize serial communication
  
  //todo use software-serial to send AT commands to GPS/LTE.
}

void loop()
{
  int winddir_raw = analogRead(PIN_WINDDIR);
  float winddir_converted = winddir_raw * 360.0 / 1023.0;  // 0-360 degrees 
  Serial.print("WInddir Raw Value: ");
  Serial.print(winddir_raw);
  Serial.print(" | converted: ");
  Serial.println(winddir_converted);
  
  rudder_angle = (uint8_t) (winddir_converted / 180.0 * 255.0);
  Serial.print("rudder angle (enc): ");
  Serial.println(rudder_angle);
  
  sheet_angle = rudder_angle;
  Serial.print("sheet angle (enc): ");
  Serial.println(sheet_angle);
  
  analogWrite(PIN_SHEET, sheet_angle);
  analogWrite(PIN_RUDDER, rudder_angle);
  
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousMillis >= wspd_interval) {
    // Disable interrupts to safely read and reset the count
    noInterrupts();
    unsigned long localCount = windspeed_counter;
    windspeed_counter = 0;
    interrupts();
    
    // Calculate Frequency in Hz
    frequency = localCount * (1000.0 / (currentMillis - previousMillis));
    previousMillis = currentMillis;
    
    // 1.492 mph = 1 switch closure/second
    wspd_mph = frequency * 1.492;
    Serial.print("WSPD Freq (Hz): ");
    Serial.print(frequency);
    Serial.print(" | MPH: ");
    Serial.println(wspd_mph);
  }
  // TODO modes
  delay(100);
}

void windspdInterrupt() {
  
  windspeed_counter++;
}