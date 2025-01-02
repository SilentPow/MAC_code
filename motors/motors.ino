#include <Servo.h>

Servo myServo;

void setup() {
  Serial.begin(9600);   // Start Serial at 9600 baud
  myServo.attach(9);    // Attach servo to pin 9
}

void loop() {
  // Check if there's incoming data on Serial
  if (Serial.available() > 0) {
    // Read the line up to '\n'
    String incoming = Serial.readStringUntil('\n');

    // Trim whitespace/newline
    incoming.trim();

    // If the command is "SPACE", then print message and move servo to 180
    if (incoming.equalsIgnoreCase("SPACE")) {
      if (myServo.read() == 180) {
        Serial.println("Space pressed!");
        myServo.write(0);
      }
      else {
        Serial.println("Space pressed!");
        myServo.write(180);
      }

    }
  }
}
