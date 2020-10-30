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
const int SERVO_START_PIN = 2; //This will correspond to the address 'a'
const int SERVOS = 2;
const int SERVO_MIN_MS = 1000;
const int SERVO_MAX_MS = 2000;
const int SERIAL_BAUD_RATE = 115200;

const int TOGGLES = 5;
const int TOGGLES_START_PIN = 9;

const int FAILSAFE_PIN = 13;
// End of configuration

const uint8_t STX = 2;
const uint8_t ETX = 3;
const int MSG_SIZE = 2;
Servo servo[SERVOS];
byte msg[MSG_SIZE];
unsigned long failsafe_timer;

void setup() {
  for (int i = 0; i < SERVOS; i++) {
    servo[i].attach(SERVO_START_PIN + i);
  }
  
  for (int i = 0; i < TOGGLES; i++) {
    pinMode(TOGGLES_START_PIN + i, OUTPUT);
    digitalWrite(TOGGLES_START_PIN + i, HIGH);
    delay(100);
  }

  delay(100);
  
  for (int i = 0; i < TOGGLES; i++) {
    digitalWrite(TOGGLES_START_PIN + i, LOW);
  }
  
  digitalWrite(FAILSAFE_PIN, HIGH);
  
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
    delay(10);
    checkFailsafe();
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
    failsafe_timer = millis();
  }
}

/*
 * Checks if FAILSAFE_TIME amount of time have passed since last read
 * if true, the failsafe will kick in.
 */
void checkFailsafe() {
  unsigned long current_time = millis();
  if (current_time - failsafe_timer > 1000) {
    servo[1].writeMicroseconds(1500);
    digitalWrite(FAILSAFE_PIN, HIGH);
  } else {
    digitalWrite(FAILSAFE_PIN, LOW); 
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
  if (msg[0] < 'a') {
    uint8_t pin = msg[0] - 'A' + TOGGLES_START_PIN;
    if (pin >= TOGGLES_START_PIN && pin <= TOGGLES_START_PIN + TOGGLES) {
      digitalWrite(pin, msg[1] == 1 ? HIGH : LOW);
    }
  } else {
    servo[msg[0] - 'a'].writeMicroseconds(map(msg[1], 0, 255, SERVO_MIN_MS, SERVO_MAX_MS));
  }
}

