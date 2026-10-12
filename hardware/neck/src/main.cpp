#include <Arduino.h>
#include <Servo.h>
#include <math.h>

// ========================================
// TOMY 2000 — NECK CONTROLLER
// Version 0.3 — Expression Library
// ========================================

// ----------------------------------------
// SERVO CONFIGURATION
// ----------------------------------------

constexpr uint8_t PAN_PIN = 9;
constexpr uint8_t TILT_PIN = 10;

constexpr int PAN_MIN = 60;
constexpr int PAN_MAX = 120;

// Calibrated safe operating limits
// Physical clearance limits: 70-100 degrees
// Includes a 5-degree safety margin

constexpr int TILT_MIN = 75;
constexpr int TILT_MAX = 95;

constexpr float PAN_CENTER = 90.0f;
constexpr float TILT_CENTER = 90.0f;

constexpr unsigned long UPDATE_INTERVAL = 20;

Servo panServo;
Servo tiltServo;

// ----------------------------------------
// MOVEMENT STATE
// ----------------------------------------

float currentPan = PAN_CENTER;
float currentTilt = TILT_CENTER;

float startPan = PAN_CENTER;
float startTilt = TILT_CENTER;

float targetPan = PAN_CENTER;
float targetTilt = TILT_CENTER;

unsigned long movementStart = 0;
unsigned long movementDuration = 800;
unsigned long activeDuration = 800;
unsigned long lastUpdate = 0;

bool isMoving = false;

// ----------------------------------------
// EXPRESSION SYSTEM
// ----------------------------------------

struct MotionStep {
    int pan;
    int tilt;
    unsigned long duration;
    unsigned long pause;
};

// CURIOUS
const MotionStep curiousSequence[] = {
    {110, 90,  900, 0},
    {110, 100, 700, 1000},
    {90,  90,  1200, 0}
};

// NOD
const MotionStep nodSequence[] = {
    {90, 100, 350, 150},
    {90, 80,  350, 150},
    {90, 90,  500, 0}
};

// SHAKE
const MotionStep shakeSequence[] = {
    {75,  90, 450, 100},
    {105, 90, 600, 100},
    {90,  90, 450, 0}
};

// SCAN
const MotionStep scanSequence[] = {
    {60,  90, 1200, 500},
    {120, 90, 2400, 500},
    {90,  90, 1200, 0}
};

// ATTENTION
const MotionStep attentionSequence[] = {
    {90, 90, 300, 0}
};

// ----------------------------------------
// ACTIVE EXPRESSION STATE
// ----------------------------------------

const MotionStep* activeSequence = nullptr;

uint8_t sequenceLength = 0;
uint8_t sequenceIndex = 0;

unsigned long pauseStart = 0;

bool waitingForPause = false;

// ----------------------------------------
// FUNCTION DECLARATIONS
// ----------------------------------------

void moveTo(float panAngle, float tiltAngle,
            unsigned long duration);

void updateMovement();
void updateExpression();
void startExpression(const MotionStep* sequence,
                     uint8_t length);

void processCommand(String command);

// ========================================
// EASING
// ========================================

float smoothstep(float t) {
    t = constrain(t, 0.0f, 1.0f);
    return t * t * (3.0f - 2.0f * t);
}

// ========================================
// MOVEMENT ENGINE
// ========================================

void moveTo(float panAngle, float tiltAngle,
            unsigned long duration) {

    panAngle = constrain(panAngle, PAN_MIN, PAN_MAX);
    tiltAngle = constrain(tiltAngle, TILT_MIN, TILT_MAX);

    startPan = currentPan;
    startTilt = currentTilt;

    targetPan = panAngle;
    targetTilt = tiltAngle;

    movementStart = millis();
    activeDuration = max(duration, 1UL);

    isMoving = true;
}

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

    panServo.write(
    constrain(round(currentPan), PAN_MIN, PAN_MAX)
    );

    tiltServo.write(
        constrain(round(currentTilt), TILT_MIN, TILT_MAX)
    );

    if (progress >= 1.0f) {

        currentPan = targetPan;
        currentTilt = targetTilt;

        isMoving = false;

        Serial.println("MOVE COMPLETE");
    }
}

// ========================================
// EXPRESSION ENGINE
// ========================================

void startExpression(const MotionStep* sequence,
                     uint8_t length) {

    activeSequence = sequence;
    sequenceLength = length;
    sequenceIndex = 0;

    waitingForPause = false;

    Serial.println("EXPRESSION STARTED");
}

void updateExpression() {

    if (activeSequence == nullptr) {
        return;
    }

    unsigned long now = millis();

    // Wait until the current movement finishes
    if (isMoving) {
        return;
    }

    // Handle pauses between movements
    if (waitingForPause) {

        if (now - pauseStart <
            activeSequence[sequenceIndex].pause) {
            return;
        }

        waitingForPause = false;
        sequenceIndex++;
    }

    // Expression finished
    if (sequenceIndex >= sequenceLength) {

        activeSequence = nullptr;

        Serial.println("EXPRESSION COMPLETE");
        return;
    }

    // Start next movement
    const MotionStep& step =
        activeSequence[sequenceIndex];

    moveTo(step.pan, step.tilt, step.duration);

    pauseStart = 0;
    waitingForPause = true;
}

// ========================================
// SERIAL COMMAND HANDLER
// ========================================

void processCommand(String command) {

    command.trim();
    command.toUpperCase();

    // New commands interrupt active expressions
    activeSequence = nullptr;
    waitingForPause = false;

    // ------------------------------------
    // EXPRESSIONS
    // ------------------------------------

    if (command == "CURIOUS") {

        startExpression(
            curiousSequence,
            sizeof(curiousSequence) /
            sizeof(MotionStep)
        );
    }

    else if (command == "NOD") {

        startExpression(
            nodSequence,
            sizeof(nodSequence) /
            sizeof(MotionStep)
        );
    }

    else if (command == "SHAKE") {

        startExpression(
            shakeSequence,
            sizeof(shakeSequence) /
            sizeof(MotionStep)
        );
    }

    else if (command == "SCAN") {

        startExpression(
            scanSequence,
            sizeof(scanSequence) /
            sizeof(MotionStep)
        );
    }

    else if (command == "ATTENTION") {

        startExpression(
            attentionSequence,
            sizeof(attentionSequence) /
            sizeof(MotionStep)
        );
    }

    // ------------------------------------
    // MANUAL MOVEMENT
    // ------------------------------------

    else if (command == "CENTER") {

        moveTo(PAN_CENTER, TILT_CENTER,
               movementDuration);

        Serial.println("CENTERING");
    }

    else if (command.startsWith("PAN ")) {

        int angle = command.substring(4).toInt();

        moveTo(angle, targetTilt, movementDuration);

        Serial.print("PAN TARGET: ");
        Serial.println(targetPan);
    }

    else if (command.startsWith("TILT ")) {

        int angle = command.substring(5).toInt();

        moveTo(targetPan, angle, movementDuration);

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

            moveTo(panAngle, tiltAngle,
                   movementDuration);

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
    Serial.println("Version 0.3 - Expression Library");
    Serial.println();

    Serial.println("COMMANDS:");
    Serial.println("PAN <angle>");
    Serial.println("TILT <angle>");
    Serial.println("LOOK <pan> <tilt>");
    Serial.println("SPEED <milliseconds>");
    Serial.println("CENTER");
    Serial.println("CURIOUS");
    Serial.println("NOD");
    Serial.println("SHAKE");
    Serial.println("SCAN");
    Serial.println("ATTENTION");
    Serial.println();

    Serial.println("READY");
}

// ========================================
// MAIN LOOP
// ========================================

void loop() {

    updateMovement();
    updateExpression();

    static String inputBuffer = "";

    while (Serial.available() > 0) {

        char incoming = Serial.read();

        if (incoming == '\n' || incoming == '\r') {

            if (inputBuffer.length() > 0) {

                processCommand(inputBuffer);
                inputBuffer = "";
            }

        } else {

            if (inputBuffer.length() < 64) {
                inputBuffer += incoming;
            }
        }
    }
}