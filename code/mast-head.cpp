#include <string>
volatile unsigned int mode = 0; 

void setup()
{
  
  pinMode(2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(2), auto_interrupt, FALLING);
  
  pinMode(3, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(3), recovery_interrupt, FALLING);
  
  Serial.begin(9600); // Initialize serial communication
  
  // TODO wait for RDY code from SIM7080 before sending commands
}

void loop()
{
  
  if (Serial.available() > 0) { // Check if data is available
    byte command = Serial.read();
    String operand = Serial.readStringUntil('\n');
    
    switch (command) {
      case 0:  // set mode
      try {
      	mode = std::stoi(operand);
        // TODO echo command ack
        break;
        catch {break;}
      case 1: // 
      default:
      	break;
    }
  }
}
}

void auto_interrupt()
{
  mode = 0;
}

void recovery_interrupt()
{
  mode = 1;
}

String send_at_command(String cmd) {
 Serial.send(cmd);
 // TODO timeout and better error handling
 String response = Serial.readStringUntil('OK');
 return response;
}

String get_gps_position() {
  String resp = send_at_command('AT+CGNSINF\n');
  // +CGNSINF:
  // 1,,,0.000000,0.000000,-18.000,,,1,,0.1,0.1,0.1,,,,9999000.0,6144.0
  //
  // OK
  // 
  // split lines
  // split line by comma and grab fields
}

void send_telemetry() {
  send_at_command('AT+SHCONF="URL",https://129.168.1.1/telemetry\n'); // configure url,bodylen, headerlen, ssl?
  //AT+SHCONN  // open connection
  // set body AT+SHBOD=<len_body>,<timeout>
  // set header AT+SHAHEAD=<type>,<value>
  // TODO change password
  // Authorization: Basic bWU6cGFzc3dvcmQ=
  // set parameters AT+SHPARA=<key>,<value>
  // set request type and execute? AT+SHREQ=<url>,3 // 3 is POST
  // get response  AT+SHREAD
  // disconnect AT+SHDISC
}