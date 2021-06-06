#include "MeOrion.h"
#include <Wire.h>
#include <SoftwareSerial.h>


MeStepper stepper(PORT_1); 
MeDCMotor motor1(M1);
MeDCMotor motor2(M2);
uint8_t motorSpeed = 100;
int trans = 150;
int pan = 5;
int tilt = 50;

void setup() {
  Serial.begin(9600);
  stepper.setMaxSpeed(2000);
  stepper.setAcceleration(7500);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available())
  {
    char a = Serial.read();
    switch(a)
    {
      case 'a':
      trans = 100;
      break;
      case 'b':
      trans = 150;
      break;
      case 'c':
      trans = 200;
      break;
      case 'd':
      trans = 250;
      break;
      case 'e':
      pan = 2;
      break;
      case 'f':
      pan = 5;
      break;
      case 'g':
      pan = 10;
      break;
      case 'h':
      pan = 15;
      break;
      case 'i':
      tilt = 25;
      break;
      case 'j':
      tilt = 50;
      break;
      case 'k':
      tilt = 75;
      break;
      case 'l':
      tilt = 100;
      break;
      case '4':
      stepper.move(pan);
      break;
      case '3':
      stepper.move(-pan);
      break;
      case '0':
      motor1.run(tilt);
      break;
      case '2':
      motor1.run(-tilt-15);
      break;
      case '5':
      motor2.run(trans);
      break;
      case '6':
      motor2.run(-trans);
      break;
      case '1':
      motor1.stop();
      break;
      case '7':
      motor2.stop();
      break;
    }
  }
  stepper.run();
}
      
