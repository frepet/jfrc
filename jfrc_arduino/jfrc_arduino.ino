/*
 * Arduino code for JF-RC
 * 
 * Reads a 4 byte serial signal and sets servos.
 *
 * Expected Serial protocol:
 *   BYTE | VALUE | NOTE
 *   -----------------------
 *     0  |   2   | Start
 *     1  |'a'-'z'| Address
 *     2  | 0-255 | Value
 *     3  |   3   | End
 *
 * Author: Fredrik Peteri, fredrik@peteri.se
 */
 
#include <Servo.h>

// Configuration
const int SERVO_START_PORT = 2; //This will correspond to the address 'a'
const int SERVOS = 2;
const int SERVO_MIN_MS = 1000;
const int SERVO_MAX_MS = 2000;
const int SERIAL_BAUD_RATE = 115200;
// End of configuration

const int STX = 2;
const int ETX = 3;
const int MSG_SIZE = 2;
Servo servo[SERVOS];
byte msg[MSG_SIZE];

void setup() {
  for (int i = 0; i < SERVOS; i++) {
    servo[i].attach(SERVO_START_PORT + i);
  }

  Serial.begin(SERIAL_BAUD_RATE);
}

/*
 * Clears the msg-buffer.
 */
void clearMsg(){
  for(int i = 0; i < MSG_SIZE; i++){
    msg[i] = 0;
  } 
}

/*
 * Reads the Serial port untill it finds the start of text (STX)
 */
void waitForMsg(){
  byte temp = Serial.read();
  
  while(temp != STX){
    temp = Serial.read();
    delay(5);
  }
}

/*
 * Reads MSG_SIZE amount of bytes from the Serial port and copies
 * them into msg if they are followed by an ETX.
 */
void readMsg(){
  byte temp[MSG_SIZE];
  for(int i = 0; i < MSG_SIZE; i++){
    temp[i] = Serial.read();
  }
  if(Serial.read() == ETX){
    memcpy(msg,temp,MSG_SIZE);
  }
}

/*
 * The program reads from serial and updates servos in an
 * endless loop.
 */
void loop() {
  clearMsg();
  waitForMsg();
  readMsg();
  
  servo[msg[0] - 'a'].writeMicroseconds(map(msg[1], 0, 255, SERVO_MIN_MS, SERVO_MAX_MS));
}

