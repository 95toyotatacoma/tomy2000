#include <Arduino.h>
#include <Servo.h>

// ========================================
// TOMY2000 - NECK CONTROLLER
// Arduino Uno R3
// ========================================

// Servo objects
Servo pan;
Servo tilt;

// Servo pins
const int PAN_PIN = 9;
const int TILT_PIN = 10;

// Starting positions
int panPosition = 90;
int tiltPosition = 90;

// Temporary testing limits
const int PAN_MIN = 60;
const int PAN_MAX = 120;

const int TILT_MIN = 70;
const int TILT_MAX = 110;


// ========================================
// SETUP
// ========================================

void setup() {

    Serial.begin(115200);

    pan.attach(PAN_PIN);
    tilt.attach(TILT_PIN);

    pan.write(panPosition);
    tilt.write(tiltPosition);

    Serial.println("================================");
    Serial.println("TOMY2000 NECK CONTROLLER");
    Serial.println("================================");

    Serial.println("Available Commands:");
    Serial.println("PAN 90");
    Serial.println("TILT 90");
    Serial.println("CENTER");

    Serial.println("Ready.");
}


// ========================================
// MAIN LOOP
// ========================================

void loop() {

    if (Serial.available() > 0) {

        String command = Serial.readStringUntil('\n');

        command.trim();
        command.toUpperCase();

        // PAN CONTROL
        if (command.startsWith("PAN ")) {

            int angle = command.substring(4).toInt();

            if (angle >= PAN_MIN && angle <= PAN_MAX) {

                panPosition = angle;
                pan.write(panPosition);

                Serial.print("Pan Position: ");
                Serial.println(panPosition);

            } else {

                Serial.println("Pan angle outside limits.");

            }
        }

        // TILT CONTROL
        else if (command.startsWith("TILT ")) {

            int angle = command.substring(5).toInt();

            if (angle >= TILT_MIN && angle <= TILT_MAX) {

                tiltPosition = angle;
                tilt.write(tiltPosition);

                Serial.print("Tilt Position: ");
                Serial.println(tiltPosition);

            } else {

                Serial.println("Tilt angle outside limits.");

            }
        }

        // CENTER BOTH SERVOS
        else if (command == "CENTER") {

            panPosition = 90;
            tiltPosition = 90;

            pan.write(panPosition);
            tilt.write(tiltPosition);

            Serial.println("Neck Centered.");
        }

        else {

            Serial.println("Unknown Command.");

        }
    }
}