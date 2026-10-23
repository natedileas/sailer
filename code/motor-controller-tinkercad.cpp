// C++ code
//
#include <avr/interrupt.h>
#include <Wire.h>

#define motorA 5
#define motorB 6
  
const int ENCODER_A = 2;
const int ENCODER_B = 3;
const byte LOW_LIMIT_PIN = 13;
const byte HIGH_LIMIT_PIN = 0xA0;
const byte i2c_addr = 51;

volatile int lastEncoded=0;
volatile long encoderValue=0;
volatile long correctEncoderValue=0;

volatile float target_angle = -100;  // at startup, set this to a low out of range value
float current_angle = 0;
float counts2angle = 1e-6;
volatile long limit_low_counts = -10000;
volatile long limit_high_counts = 10000;

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(ENCODER_A, INPUT);
  pinMode(ENCODER_B, INPUT);
  digitalWrite(ENCODER_A, HIGH);
  digitalWrite(ENCODER_B, HIGH);
  pinMode(LOW_LIMIT_PIN, INPUT);
  pinMode(HIGH_LIMIT_PIN, INPUT);
  
   pinMode(motorA,OUTPUT);
   pinMode(motorB,OUTPUT);
 
  attachInterrupt(digitalPinToInterrupt(ENCODER_A), encoder_interrupt, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENCODER_B), encoder_interrupt, CHANGE);
  
   // https://thewanderingengineer.com/2014/08/11/arduino-pin-change-interrupts/
  cli();
  PCICR |= 0b111;
  PCMSK0 |= 0b100000; // pin 13
  PCMSK1 |= 0b1;   // pin A0
  sei();
  
  Serial.begin(9600);
  Wire.begin(i2c_addr);
  Wire.onRequest(i2c_request);
  Wire.onReceive(i2c_receive);
}

void i2c_receive(int numBytes) {
  while (Wire.available()) {
    // TODO if we are fully calibrated
    float tgt = Wire.read(4);
    target_angle = tgt;
  }
}

void i2c_request(int numBytes) {
  Wire.write((char*)current_angle);
}

ISR (PCINT0_vect) 
{    
    // manage for PCINT for D8 to D13
  limit_low_interrupt();
}

ISR (PCINT1_vect) 
{
    // manage PCINT for A0 to A5
  limit_high_interrupt();
}  

void loop()
{
  
  correctEncoderValue = encoderValue/4;  // divide by 4 because the interrupt will trigger 4 times for every pulse
  Serial.print("correctEncoderValue=");
  Serial.print(correctEncoderValue);
  
  counts2angle = 180 / (float)(limit_high_counts - limit_low_counts)/ 10.0;
  Serial.print("counts2angle=");
  Serial.print(counts2angle);
  current_angle = counts2angle * encoderValue;
  Serial.print("current_angle=");
  Serial.print(current_angle);
  /*
  Serial.print("target_angle=");
  Serial.print(target_angle);
  Serial.print("limit_high_counts=");
  Serial.print(limit_high_counts);
  Serial.print("limit_low_counts=");
  Serial.print(limit_low_counts);
  */
  
  if (current_angle > target_angle && correctEncoderValue > limit_low_counts) {
    // reverse
    Serial.println("direction=reverse");
   	analogWrite(motorA,127); // todo scale speed by distance from target?
   digitalWrite(motorB,HIGH);
  } 
  else if (current_angle <= target_angle && correctEncoderValue < limit_high_counts)
  {
    Serial.println("direction=forward");
    // forward
   analogWrite(motorA,127);
   digitalWrite(motorB,LOW);
  }
  else {
    Serial.println("direction=stop");
    // we are out of bounds, so stop
   analogWrite(motorA,0);
   digitalWrite(motorB,HIGH);
  }
  
   delay(100);
}

void limit_high_interrupt() {
	limit_high_counts = encoderValue / 4;  
  	if (target_angle > 90) {
      	// we have finished our startup search for the upper limit.
        // Set the target angle to neutral
    	target_angle = 0;
  	}
}

void limit_low_interrupt() {
  limit_low_counts = encoderValue / 4;
  if (target_angle < -90) { 
    // we have finished our startup search for the lower limit. 
    // Set the target angle high out of range so that we search for the upper limit
    target_angle = 100;
  }
}

void encoder_interrupt() {
  int MSB = digitalRead(ENCODER_A); //MSB = most significant bit
  int LSB = digitalRead(ENCODER_B); //LSB = least significant bit
   int encoded = (MSB << 1) |LSB; //converting the 2 pin value to single number
  int sum  = (lastEncoded << 2) | encoded; //adding it to the previous encoded value
 
  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderValue ++;
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderValue --;
 
  lastEncoded = encoded; //store this value for next time
}
