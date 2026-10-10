# TOMY2000

TOMY2000 is a compact robot-neck controller project built around an Arduino Uno and two hobby servos. The firmware accepts serial commands to move the pan and tilt axes, allowing simple head motion control from a host system or controller.

## Project structure

- `hardware/neck/` — PlatformIO project for the neck controller firmware
- `hardware/servo_test/` — scratch/testing files for servo experimentation

## Hardware

- Microcontroller: Arduino Uno R3
- Servos: pan and tilt rotation servos
- Control interface: serial over USB at 115200 baud

## Serial commands

The firmware supports:

- `PAN 90` — move the pan servo to 90 degrees
- `TILT 90` — move the tilt servo to 90 degrees
- `CENTER` — reset both servos to the center position

The current motion ranges are constrained for safety:

- Pan: 60° to 120°
- Tilt: 70° to 110°

## PlatformIO setup

From the repo root:

```bash
cd hardware/neck
pio run
pio run --target upload
```

## Development notes

This repository is intentionally lightweight and geared toward iterative hardware prototyping. The neck firmware is the main living project, while the servo test area remains separate as experimental scratch work.
