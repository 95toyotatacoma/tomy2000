# TOMY — Hardware Interface & Sensor Allocation Matrix

**Project:** TOMY 2000 | Proctor House Studio  
**Date:** 2026-10-20  
**Status:** Planning and handoff; existing working connections explicitly identified  
**Purpose:** Track physical placement, electrical interfaces, software ownership, and verification status for Tomy's sensors, cameras, displays, and controllers. Preserve the original monochrome OLED multiplexer configuration for conversion into a rear diagnostic panel without disturbing the working SPI5 RGB eyes.

> **Evidence labels:** **Verified in code** = directly supported by the original scripts as described in the handoff; **Previously operational / reported** = described as having worked, but not retested now; **Verified in engineering log** = documented working test; **Planned** = proposal only; **Needs verification** = not established by the supplied records. A planned connection is not an installed connection.

## 1. Handoff recap and architectural decisions

- Tomy's **original two monochrome eyes** were **128 × 64 SSD1306 I²C OLEDs**, each at address **`0x3C`**, controlled via a **PCA9548A HW-617** eight-channel I²C multiplexer. The original Python code assigns **left eye to channel 0** and **right eye to channel 1**. These were previously operational; their current electrical condition is untested.
- Tomy's **current two Waveshare 1.5-inch 128 × 128 SSD1351 RGB eyes** are operational on **Raspberry Pi 5 SPI5**. This is a separate interface and must be preserved.
- The monochrome OLEDs are to become **three rear-mounted diagnostic displays** in a horizontal row beneath the neck: **POWER**, **SYSTEM**, and **HEALTH**. The third display is planned for multiplexer channel 2.
- The photographed purple multiplexer board was identified in the handoff as **PCA9548A HW-617**, although the software imports the compatible `adafruit_tca9548a` library. Do not assume every spare breakout has the same chip or voltage arrangement without inspection.
- The proposed architecture uses **a dedicated rear-display multiplexer**. A **second, separately addressed multiplexer** is proposed for five VL53L0X distance sensors. Approximately six multiplexer boards are reportedly on hand; count and markings still need verification.
- **Do not assume** that camera connections, sensor placements, battery telemetry, or third rear OLED functionality have already been implemented.

## 2. Physical and interface allocation matrix

| ID | Hardware | Proposed / existing physical location | Interface and host | Assignment | Status / verification |
|---|---|---|---|---|---|
| EYE-L | Waveshare 1.5-inch SSD1351 RGB OLED | Left eye | Pi 5 SPI5; physical left/right mapping to CE device TBD | Expression, gaze, blink | **Verified in engineering log**: both eyes work; physical mapping needs labeling |
| EYE-R | Waveshare 1.5-inch SSD1351 RGB OLED | Right eye | Pi 5 SPI5; physical left/right mapping to CE device TBD | Expression, gaze, blink | **Verified in engineering log** |
| DISP-01 | SSD1306 128 × 64 monochrome OLED (former left eye) | Upper back, left | Pi 5 I²C → PCA9548A display mux CH0; `0x3C` | POWER | **Verified in code** channel assignment; rear installation **planned** |
| DISP-02 | SSD1306 128 × 64 monochrome OLED (former right eye) | Upper back, center | Pi 5 I²C → PCA9548A display mux CH1; `0x3C` | SYSTEM | **Verified in code** channel assignment; rear installation **planned** |
| DISP-03 | Third 0.96-inch 128 × 64 OLED (candidate ELEGOO) | Upper back, right | Pi 5 I²C → PCA9548A display mux CH2; expected `0x3C` | HEALTH | **Planned**; controller/address and operation not verified |
| CAM-01 | Raspberry Pi Camera Module V2, visible-light | Upper head dome, center (per sketch) | CSI camera interface; Pi 5 | Social/primary vision | **Planned**; connector assignment TBD |
| CAM-02 | Raspberry Pi Camera Module 2 NoIR | Head, position TBD | CSI camera interface; Pi 5 or alternate architecture | Low-light/near-IR vision | **Planned**; IR illumination may be required |
| CAM-03 | Raspberry Pi Camera Module V2, visible-light | Front chassis, candidate | CSI camera interface; host TBD | Navigation vision | **Planned**; Pi 5 has only two MIPI connectors |
| TOF-01 | VL53L0X | Left ear opening (~36 mm) | Pi 5 I²C → sensor mux CH0 | Left clearance | **Planned** |
| TOF-02 | VL53L0X | Right ear opening (~36 mm) | Pi 5 I²C → sensor mux CH1 | Right clearance | **Planned** |
| TOF-03 | VL53L0X | Upper front torso | Pi 5 I²C → sensor mux CH2 | Body-level obstacles | **Planned** |
| TOF-04 | VL53L0X | Front lower chassis | Pi 5 I²C → sensor mux CH3 | Near-front obstacles | **Planned** |
| TOF-05 | VL53L0X | Rear lower chassis | Pi 5 I²C → sensor mux CH4 | Reversing clearance | **Planned** |
| US-01–03 | Three ultrasonic sensors (previously HC-SR04) | Front center, front-left, front-right chassis | Arduino Nano digital I/O proposed | Obstacle detection | **Planned**; stagger triggers; protect 3.3 V logic if interfacing with Pi |
| PIR-01–02 | Two pyroelectric motion sensors | Front and rear torso candidates | Arduino or Pi GPIO TBD | Motion/presence events | **Planned**; exact modules and output levels TBD |
| IR-01–02 | Two additional IR motion/proximity sensors from earlier inventory | TBD | TBD | Supplemental proximity/motion | **Needs verification**: confirm these are distinct from PIR units |
| ALS-01 | TSL2591 ambient light sensor | Top of head, candidate | Pi 5 I²C, direct bus if address-compatible | Ambient light; display/vision policy | **Planned** |
| IMU-01 | BerryIMUv3 (IMU + barometer) | Rigidly mounted in lower torso | Pi 5 I²C, direct bus if compatible | Acceleration, orientation, pressure | **Planned**; avoid magnetic interference |
| AUDIO-01 | ReSpeaker 2-Mic Pi HAT V1.0 | Pi 5 / upper body | Pi HAT interfaces | Hearing | **Installed/reported**; audio operation not fully validated in latest milestone |
| CTRL-01 | Raspberry Pi 5 | Main electronics bay | Host controller | Vision, UI, personality, orchestration | **Verified operational** |
| CTRL-02 | Arduino (Nano previously reported) | Electronics bay | USB serial `/dev/ttyACM0`, 115200 in older scripts | Neck/low-level control | **Previously prototyped**; current port and firmware TBD |
| CTRL-03 | Raspberry Pi 3 spare | Not allocated | TBD | Reserve only | **Available/reported**; not required in baseline design |
| DRIVE-01 | Two 12 V DC gear motors + motor drivers | Tracked chassis | Arduino → motor driver, TBD | Locomotion | **In development** |
| SERVO-01+ | Neck/arm servos | Head and arms | Arduino / servo control, TBD | Pan, tilt, gestures | **Previously prototyped / planned**; safe limits TBD |
| UI-01 | Larger chest touchscreen | Front torso | Pi 5 display interface TBD | Main user interface | **Planned / model TBD** |

## 3. Existing, tested RGB eye wiring — preserve unchanged

The engineering-state log records the following **BCM GPIO** and **physical header pins** for the working RGB eyes:

| Signal | Eye 1 — SPI5 CE0 | Eye 2 — SPI5 CE1 |
|---|---|---|
| VCC | Pi 3.3 V, physical pin 1 | Pi 3.3 V, physical pin 17 |
| GND | Physical pin 6 | Physical pin 9 |
| MOSI / DIN | GPIO 14, physical pin 8 | Shared GPIO 14, physical pin 8 |
| SCLK / CLK | GPIO 15, physical pin 10 | Shared GPIO 15, physical pin 10 |
| CS | GPIO 12, physical pin 32 | GPIO 26, physical pin 37 |
| DC | GPIO 25, physical pin 22 | GPIO 22, physical pin 15 |
| RST | GPIO 24, physical pin 18 | GPIO 23, physical pin 16 |
| Linux SPI device | `/dev/spidev5.0` | `/dev/spidev5.1` |

- Existing configuration: `dtparam=spi=on`, `dtoverlay=spi5-2cs` in `/boot/firmware/config.txt`.
- Keep existing `software/eyes/` code and eye pin allocation intact. The ReSpeaker HAT's APA102 LEDs previously conflicted with experiments on SPI0; SPI5 resolved the observed display-test issue.
- Physical left/right correspondence to Eye 1/Eye 2 still needs labeling.

## 4. Original monochrome OLED I²C architecture — preserve channel mapping

### Raspberry Pi 5 to display multiplexer (standard pins; physical wiring unverified)

| Pi signal | Physical header pin | PCA9548A HW-617 pin |
|---|---:|---|
| 3.3 V | 1 or 17 (as available and within rail budget) | VIN/VCC (verify actual board labeling) |
| Ground | Any suitable GND | GND |
| GPIO 2 / SDA1 | 3 | SDA |
| GPIO 3 / SCL1 | 5 | SCL |

**Important:** The original code uses `board.I2C()`, but does **not** prove the historical jumper-to-header wiring. Verify actual pins, supply voltage, pull-ups, and board labeling before power-up.

### Display multiplexer (PCA9548A HW-617, proposed address `0x70`)

| Channel | Output pins | OLED | OLED I²C address | Rear function | Evidence |
|---|---|---|---|---|---|
| 0 | SD0 / SC0 | Original LEFT eye | `0x3C` | POWER | Original code mapping verified |
| 1 | SD1 / SC1 | Original RIGHT eye | `0x3C` | SYSTEM | Original code mapping verified |
| 2 | SD2 / SC2 | Third monochrome OLED | `0x3C` expected | HEALTH | Planned; scan to confirm |
| 3–7 | SD3/SC3 … SD7/SC7 | Unassigned | — | Expansion | Available |

Each display also requires **VCC and GND**. The multiplexer switches **SDA/SCL**, not the power rails. Displays on different channels may use the same `0x3C` address and still be updated independently.

### Proposed sensor multiplexer (second board, candidate address `0x71`)

| Channel | Proposed device |
|---|---|
| 0 | VL53L0X left ear |
| 1 | VL53L0X right ear |
| 2 | VL53L0X upper torso |
| 3 | VL53L0X front chassis |
| 4 | VL53L0X rear chassis |
| 5–7 | Available |

Set the second breakout's address-select pins per its actual silkscreen/datasheet (commonly A0 asserted for `0x71`). **Both multiplexer addresses are unverified until scanned.** The BerryIMUv3 and TSL2591 may share the upstream I²C bus if addresses, bus loading, and electrical levels permit. Two multiplexers improve channel organization but still share upstream SDA/SCL.

### Topology

```text
Raspberry Pi 5
  |-- SPI5 -------------------- RGB EYE 1 / RGB EYE 2  [WORKING]
  |
  |-- I2C SDA1/SCL1 ----------+-- PCA9548A DISPLAY MUX (0x70 proposed)
  |                          |     CH0 -> OLED POWER  (0x3C)
  |                          |     CH1 -> OLED SYSTEM (0x3C)
  |                          |     CH2 -> OLED HEALTH (0x3C)
  |                          |
  |                          +-- TCA/PCA9548A SENSOR MUX (0x71 proposed)
  |                          |     CH0..CH4 -> five VL53L0X
  |                          |
  |                          +-- TSL2591 and BerryIMUv3 (if compatible)
  |
  |-- MIPI camera ports ------ up to two direct CSI camera connections
  |-- USB serial ------------ Arduino (historically /dev/ttyACM0)
  +-- other interfaces ------ audio, chest UI, etc. (verify allocation)
```

## 5. Original Python code and proposed software ownership

The supplied handoff states that `diagonal_gaze.py`, `coordinated_gaze.py`, and `autonomous_tomy.py` share this initialization:

```python
import board
import adafruit_tca9548a
import adafruit_ssd1306

i2c = board.I2C()
tca = adafruit_tca9548a.TCA9548A(i2c)
left_eye = adafruit_ssd1306.SSD1306_I2C(128, 64, tca[0], addr=0x3C)
right_eye = adafruit_ssd1306.SSD1306_I2C(128, 64, tca[1], addr=0x3C)
```

The library name `adafruit_tca9548a` is compatible with the reported PCA9548A chip. The historical scripts also use Arduino serial at `/dev/ttyACM0`, 115200 baud, for neck experiments; **Arduino is not required to render rear diagnostic OLED content**.

Proposed new code, preserving the repository's existing `software/` structure:

```text
software/
  diagnostics/
    diagnostic_displays.py   # initialize mux and independently render 3 OLEDs
    power_monitor.py         # battery/power readings when hardware exists
    system_monitor.py        # CPU temp, RAM, CPU load from Linux
    health_monitor.py        # sensor/service/communication health checks
```

The rear diagnostics should run as a separate process from RGB eye animations. Coordinate access if other programs also use the same multiplexer; avoid running old eye scripts and diagnostic software against the same OLEDs at once.

## 6. Diagnostic display definitions

| Display | Initial implementation | Future implementation / dependency |
|---|---|---|
| **POWER** (CH0) | Label and placeholder/unavailable telemetry | Battery voltage, state of charge, power consumption; requires suitable battery monitor/fuel gauge and calibration |
| **SYSTEM** (CH1) | CPU temperature, memory utilization, CPU activity from Linux | Additional compute and application performance metrics |
| **HEALTH** (CH2) | I²C device presence, service status, sensor connectivity where measurable | Fault summaries, drive/servo health, subsystem diagnostics; requires defined health checks |

Do not display fabricated battery percentages or claim a subsystem is healthy merely because no error has been reported. A previously discussed **personality/behavioral-state** display is an optional future mode, not part of the three-display POWER / SYSTEM / HEALTH handoff assignment.

## 7. Electrical, mechanical, and software constraints

1. **Power down the Pi** before changing any wiring. Confirm the exact breakout chip, pin labels, address jumpers, and OLED supply requirements.
2. The Pi GPIO bus is **3.3 V logic**; do not expose SDA/SCL or other Pi pins to 5 V pull-ups. Inspect onboard breakout pull-ups and voltage arrangements.
3. Check the combined **3.3 V rail budget** for both RGB eyes, multiplexers, OLEDs, sensors, and any HAT-connected loads; use appropriately regulated distribution.
4. Keep motor/servo supply paths separate from GPIO power; design grounding, noise control, and motor-stop behavior deliberately.
5. Design a **removable, three-window rear panel** beneath the neck with display mounts, cable strain relief, service access, and clearance for neck pan/tilt.
6. Cameras are **not installed in the eyes**: both eye cavities are occupied by functioning RGB OLED displays.
7. The Pi 5 has **two MIPI camera/display connectors**, not three independent native CSI inputs. Decide which two cameras need simultaneous operation before allocating camera ports; the spare Pi 3 is not yet part of the baseline architecture.
8. The NoIR camera is sensitive to near-infrared light, **not a thermal camera**. Infrared illumination may be necessary in darkness.
9. Do not infer that ultrasonic sensors, PIR sensors, ToF sensors, battery monitoring, or chassis camera are already wired simply because their locations are proposed here.

## 8. Bench verification and implementation sequence

- [ ] Inventory the actual multiplexers; photograph/record chip markings and address-selection pads.
- [ ] With power off, trace and label Pi → PCA9548A **VIN/GND/SDA/SCL** and OLED CH0/CH1 wiring; do not rely on jumper colors.
- [ ] Confirm the original two SSD1306 boards' voltage requirements and physical condition.
- [ ] Verify the existing RGB eyes still work **before** touching I²C wiring; record baseline.
- [ ] Enable/check Pi I²C configuration and scan upstream bus (e.g., `i2cdetect -y 1`), expecting a mux at a scanned address such as `0x70` rather than assuming it.
- [ ] Run a minimal CH0-only OLED test; then CH1-only; confirm independent rendering.
- [ ] Add the third display on CH2; verify its controller and address by test.
- [ ] Implement `system_monitor.py` first using real CPU/RAM readings.
- [ ] Add `diagnostic_displays.py` and render POWER/SYSTEM/HEALTH independently.
- [ ] Validate operation **simultaneously with SPI5 RGB eye animation**; watch power/CPU behavior.
- [ ] Wire and scan the second mux at a distinct address; test each VL53L0X individually.
- [ ] Define battery-monitor hardware and sensor-health criteria before claiming live POWER/HEALTH metrics.
- [ ] Build rear panel prototype and verify neck clearance, readability, strain relief, and service access.
- [ ] Record tested wiring and software commands in `ENGINEERING_STATE.md` after validation.

## 9. Source and uncertainty notes

**Based on:** User-provided *TOMY — I²C Multiplexer & Rear Diagnostic Display Handoff* dated 2026-10-20; the user's camera/display photos and rear-panel sketch; and the supplied `ENGINEERING_STATE(2).md` dated 2026-10-20.

**Directly supported by handoff's description of original code:** `board.I2C()`, `adafruit_tca9548a`, `adafruit_ssd1306`, channel 0/1 assignments, `0x3C`, 128 × 64, and historic Arduino serial settings. The original scripts were **not independently re-executed** in preparing this document.

**Supported by engineering-state log:** Two working SSD1351 RGB OLEDs on SPI5 with the pin mapping shown above; the ReSpeaker HAT's earlier SPI0 interference; neck integration pending; RGB eye feature branch status.

**Still unverified:** Physical historical I²C jumpers, live multiplexer address, OLED condition, third OLED controller/address, current Pi power budget, sensor installation and wiring, camera connection allocation, and final rear panel dimensions.

---

### Next-session handoff

Tomy's original SSD1306 128 × 64 monochrome OLED eyes used a PCA9548A HW-617 I²C multiplexer: former left eye on CH0 and former right eye on CH1, each at `0x3C`. Reuse these as rear **POWER** and **SYSTEM** displays, add a third **HEALTH** display on CH2, and retain the existing two working SSD1351 RGB eyes on SPI5. Begin with a power-off wiring audit and an I²C scan; do not disturb the tested SPI5 setup. A second, separately addressed multiplexer is proposed for five VL53L0X sensors. All proposed locations and connections must be verified before being marked installed.
