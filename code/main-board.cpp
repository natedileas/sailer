#include <Wire.h>

const int PIN_WINDDIR = 14; // A0
const int PIN_WINDSPD = 2;
const int PIN_WATER_DETECT = 3;
const int PIN_TEMP_1 = 4;

volatile int windspeed_counter = 0;
unsigned long previousMillis = 0;
const long wspd_interval = 1000; // 1 second

float WSPD_MAX = 15; // MPH
float FURL_START = 10; // MPH

uint8_t mode = 0; // 0:recovery, 1:normal
float wspd_mph;
float winddir; // wind direction, ccw degrees from center line, 0-360
float rudderangle_tgt = 0; // -90 to 90, ccw degrees from center line
float rudderangle_cur = 0;
float sheetangle_tgt = 0; // -90 to 90, ccw degrees from center line.
float sheetangle_cur = 0;
float furlpct_tgt = 0; // 0-100, 0 is fully furled, 100 is fully extended
float furlpct_cur = 0;
float heading_tgt = 0; // [cw degrees from N 0-360]
float heading_cur = 0;

void setup()
{
  pinMode(PIN_WINDDIR, INPUT);
  pinMode(PIN_WINDSPD, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_WINDSPD), windspdInterrupt, FALLING);
  
  Serial.begin(9600); // Initialize serial communication
  
  Wire.begin();
}

void loop()
{
  // TODO read from i2c IMU
  //   TODO if crazy angles, enter recovery mode
  // TODO read from i2c rudder
  // TODO read from i2c furl
  // TODO read from i2c boom/sheet
  // TODO read from i2c battery?
  //  TODO if low battery, enter recovery mode

  // TODO read from uart, respond to commands

  int winddir_raw = analogRead(PIN_WINDDIR);
  winddir = winddir_raw * 360.0 / 1023.0;  // 0-360 degrees 
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

  // sailing
  // TODO command i2c sheet angle
  // set based on wind angle
  if (winddir < 90 || winddir > 270) {
    // upwind
  }
  else {
    // downwind
  }

  // TODO command i2c furl angle
  if (wspd_mph <  FURL_START) {
    furlpct_tgt = 100;
  }
  elif (wspd_mph > WSPD_MAX) {
    furlpct_tgt = 0;
  }
  else {
    furlpct_tgt = 100 * (1- (wspd_mph-FURL_START)/ (WSPD_MAX-FURL_START));
  }

  // TODO command i2c rudder angle
  // PID rudder from tgt/cur heading
  
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousMillis >= wspd_interval) {
    // Disable interrupts to safely read and reset the count
    noInterrupts();
    unsigned long localCount = windspeed_counter;
    windspeed_counter = 0;
    interrupts();
    
    // Calculate Frequency in Hz
    float frequency = localCount * (1000.0 / (currentMillis - previousMillis));
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