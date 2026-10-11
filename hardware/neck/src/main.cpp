#include <Arduino.h>
#include <Servo.h>
#include <math.h>

// ========================================
// FUNCTION DECLARATIONS
// ========================================

void moveTo(float panAngle, float tiltAngle);

// ========================================
// TOMY 2000 — NECK CONTROLLER
// Version 0.2 — Natural Movement
// ========================================

// Servo pins
constexpr uint8_t PAN_PIN = 9;
constexpr uint8_t TILT_PIN = 10;

// Movement limits
constexpr int PAN_MIN = 60;
constexpr int PAN_MAX = 120;

constexpr int TILT_MIN = 70;
constexpr int TILT_MAX = 110;

// Default positions
constexpr float PAN_CENTER = 90.0f;
constexpr float TILT_CENTER = 90.0f;

// Movement settings
constexpr unsigned long UPDATE_INTERVAL = 20;
unsigned long movementDuration = 800;

// Servo objects
Servo panServo;
Servo tiltServo;

// Current positions
float currentPan = PAN_CENTER;
float currentTilt = TILT_CENTER;

// Starting positions
float startPan = PAN_CENTER;
float startTilt = TILT_CENTER;

// Target positions
float targetPan = PAN_CENTER;
float targetTilt = TILT_CENTER;

// Movement state
unsigned long movementStart = 0;
unsigned long activeDuration = 800;
unsigned long lastUpdate = 0;

bool isMoving = false;

// ========================================
// BEHAVIOR CONTROLLER
// ========================================

enum Behavior {
    NONE,
    CURIOUS
};

Behavior activeBehavior = NONE;

uint8_t behaviorStep = 0;
unsigned long behaviorTimer = 0;
unsigned long savedMovementDuration = 800;

// ========================================
// CURIOUS BEHAVIOR
// ========================================

void updateBehavior() {

    if (activeBehavior != CURIOUS) {
        return;
    }

    unsigned long now = millis();

    switch (behaviorStep) {

        case 0:
            // Notice something to the right
            movementDuration = 900;
            moveTo(110, 90);

            behaviorStep = 1;
            break;

        case 1:
            // Wait until the turn finishes
            if (!isMoving) {
                movementDuration = 700;
                moveTo(110, 100);

                behaviorStep = 2;
            }
            break;

        case 2:
            // Wait until the tilt finishes
            if (!isMoving) {
                behaviorTimer = now;
                behaviorStep = 3;
            }
            break;

        case 3:
            // Hold the curious pose
            if (now - behaviorTimer >= 1000) {
                movementDuration = 1200;
                moveTo(90, 90);

                behaviorStep = 4;
            }
            break;

        case 4:
        if (!isMoving) {
            movementDuration = savedMovementDuration;

            activeBehavior = NONE;
            behaviorStep = 0;

            Serial.println("CURIOUS COMPLETE");
        }
        break;
    }
}

// ========================================
// EASING FUNCTION
// ========================================

float smoothstep(float t) {
    t = constrain(t, 0.0f, 1.0f);
    return t * t * (3.0f - 2.0f * t);
}

// ========================================
// START MOVEMENT
// ========================================

void moveTo(float panAngle, float tiltAngle) {

    // Clamp requested angles
    panAngle = constrain(panAngle, PAN_MIN, PAN_MAX);
    tiltAngle = constrain(tiltAngle, TILT_MIN, TILT_MAX);

    // Capture current positions
    startPan = currentPan;
    startTilt = currentTilt;

    // Set new targets
    targetPan = panAngle;
    targetTilt = tiltAngle;

    // Start timer
    movementStart = millis();
    activeDuration = movementDuration;

    isMoving = true;
}

// ========================================
// UPDATE MOVEMENT
// ========================================

void updateMovement() {

    if (!isMoving) return;

    unsigned long now = millis();

    if (now - lastUpdate < UPDATE_INTERVAL) {
        return;
    }

    lastUpdate = now;

    float progress =
        float(now - movementStart) / float(activeDuration);

    progress = constrain(progress, 0.0f, 1.0f);

    float eased = smoothstep(progress);

    currentPan =
        startPan + (targetPan - startPan) * eased;

    currentTilt =
        startTilt + (targetTilt - startTilt) * eased;

    panServo.write(round(currentPan));
    tiltServo.write(round(currentTilt));

    if (progress >= 1.0f) {
        currentPan = targetPan;
        currentTilt = targetTilt;
        isMoving = false;

        Serial.println("MOVE COMPLETE");
    }
}

// ========================================
// SERIAL COMMAND HANDLER
// ========================================

void processCommand(String command) {

    command.trim();
    command.toUpperCase();

    // Manual commands cancel any active behavior.
    // CURIOUS is handled separately below.
   // Manual commands cancel autonomous behaviors
    if (command != "CURIOUS") {

        if (activeBehavior != NONE) {
            movementDuration = savedMovementDuration;
        }

        activeBehavior = NONE;
        behaviorStep = 0;
    }

    if (command == "CURIOUS") {

    // Preserve the user's movement speed
    if (activeBehavior == NONE) {
        savedMovementDuration = movementDuration;
    }

    activeBehavior = CURIOUS;
    behaviorStep = 0;

    Serial.println("CURIOUS STARTED");
    return;
    }

    if (command == "CENTER") {

        moveTo(PAN_CENTER, TILT_CENTER);

        Serial.println("CENTERING");
    }

    else if (command.startsWith("PAN ")) {

        int angle = command.substring(4).toInt();

        moveTo(angle, targetTilt);

        Serial.print("PAN TARGET: ");
        Serial.println(targetPan);
    }

    else if (command.startsWith("TILT ")) {

        int angle = command.substring(5).toInt();

        moveTo(targetPan, angle);

        Serial.print("TILT TARGET: ");
        Serial.println(targetTilt);
    }

    else if (command.startsWith("LOOK ")) {

        int separator = command.indexOf(' ', 5);

        if (separator > 0) {

            int panAngle =
                command.substring(5, separator).toInt();

            int tiltAngle =
                command.substring(separator + 1).toInt();

            moveTo(panAngle, tiltAngle);

            Serial.println("LOOKING");
        }
    }

    else if (command.startsWith("SPEED ")) {

        unsigned long duration =
            command.substring(6).toInt();

        movementDuration =
            constrain(duration, 200UL, 5000UL);

        Serial.print("DURATION: ");
        Serial.print(movementDuration);
        Serial.println(" ms");
    }

    else {
        Serial.println("UNKNOWN COMMAND");
    }
}

// ========================================
// SETUP
// ========================================

void setup() {

    Serial.begin(115200);

    panServo.attach(PAN_PIN);
    tiltServo.attach(TILT_PIN);

    panServo.write(PAN_CENTER);
    tiltServo.write(TILT_CENTER);

    Serial.println();
    Serial.println("TOMY 2000 NECK CONTROLLER");
    Serial.println("Version 0.2 — Natural Movement");
    Serial.println();

    Serial.println("COMMANDS:");
    Serial.println("PAN <angle>");
    Serial.println("TILT <angle>");
    Serial.println("LOOK <pan> <tilt>");
    Serial.println("SPEED <milliseconds>");
    Serial.println("CENTER");
    Serial.println("CURIOUS");
    Serial.println();
    Serial.println("READY");
}

// ========================================
// MAIN LOOP
// ========================================

void loop() {

    updateMovement();
    updateBehavior();

    static String inputBuffer = "";

    while (Serial.available() > 0) {

        char incoming = Serial.read();

        // Process the command only when Enter is pressed
        if (incoming == '\n' || incoming == '\r') {

            if (inputBuffer.length() > 0) {
                processCommand(inputBuffer);
                inputBuffer = "";
            }

        } else {

            // Collect characters as they arrive
            if (inputBuffer.length() < 64) {
                inputBuffer += incoming;
            }
        }
    }
}