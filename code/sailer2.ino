volatile unsigned int mode = 0; 

void setup()
{
  
  pinMode(2, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(2), auto_interrupt, FALLING);
  
  pinMode(3, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(3), recovery_interrupt, FALLING);
  
  Serial.begin(9600); // Initialize serial communication
  
}

void loop()
{
  if (Serial.available() > 0) { // Check if data is available
    String incomingData = Serial.readString(); // Read the incoming data
    Serial.print("Logged: ");
    Serial.println(incomingData); // Log it back to Serial Monitor
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