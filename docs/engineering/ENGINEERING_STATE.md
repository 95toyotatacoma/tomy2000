# TOMY — Engineering State & Development Log

**Project:** TOMY 2000 | Proctor House Studio  
**Repository:** https://github.com/95toyotatacoma/tomy2000  
**Status as of:** 2026-10-20  
**Document purpose:** Record verified build state separately from plans, preserve engineering decisions, and provide a reliable starting point for future development sessions.

> **Evidence convention:** **Verified** = demonstrated in a hands-on test or Git output; **Reported** = owner-described physical condition or inventory; **Planned** = not yet implemented or validated; **Needs verification** = details not recently tested. Never interpret a proposed component or architecture as installed.

## 1. Executive status

TOMY is a retrofitted vintage TOMY Omnibot 2000 intended to become an expressive, perceptive, playful robotic character. The most recent verified milestone is **two independently addressed 128 × 128 RGB OLED eyes with coordinated gaze and blinking** on a Raspberry Pi 5. The eye animation was tested successfully on 2026-10-19. The neck has previous experimental control scripts but **has not yet been integrated with the new RGB eye animation**.

| Subsystem | State | Evidence / caveat |
| --- | --- | --- |
| Raspberry Pi 5 | **Verified operational** | Ran SPI5 display tests and Python animation. |
| Dual Waveshare 1.5-inch SSD1351 RGB OLEDs | **Verified operational** | Both screens independently tested; coordinated gaze and blink demonstrated. |
| SPI5 interface | **Verified operational** | `/dev/spidev5.0` and `/dev/spidev5.1` open successfully. |
| ReSpeaker 2-Mic Pi HAT V1.0 (KS0314) | **Installed/reported** | Eye tests no longer illuminate its LEDs; microphone audio function not validated in this milestone. |
| Neck pan/tilt and Arduino control | **Previously prototyped; integration pending** | Existing neck/gaze scripts preserved. Servo motion and safe limits need renewed validation. |
| Drive/tread system | **In development** | Mechanical/electrical integration and driving tests not verified here. |
| Arms and claws | **Repair/redesign in progress** | Prior damage and joint problems reported. |
| Eye accent rings | **Planned** | White LEDs, printed diffusers, MOSFET drivers; no completed circuit or validated component ratings. |
| GitHub version control | **Verified** | RGB code committed and pushed to `feature/rgb-eyes` branch. Not yet merged into `main`. |

## 2. Hardware inventory and physical condition

### Confirmed or previously reported components

- Original **TOMY Omnibot 2000** shell, remote, tray, and manual; robot has undergone substantial disassembly, cleaning, sanding, and preparation for refinishing.
- **Raspberry Pi 5** as high-level controller.
- **Arduino** used in prior neck-servo experiments; confirm exact board and current firmware before rewiring.
- **Two Waveshare 1.5-inch 128 × 128 SSD1351 SPI RGB OLED displays**, now functioning.
- **KEYESTUDIO ReSpeaker 2-Mic Pi HAT V1.0 (KS0314)**; the HAT has onboard APA102 LEDs that conflicted with earlier SPI0 display experiments.
- Prior inventory/plans include light, distance, motion, and inertial sensors; DC gear motors, motor drivers, servos, speaker, and battery/regulator components. **Do not assume every item is installed or connected.** Reconcile against physical inventory before designing wiring.
- White through-hole LEDs are on hand for proposed eye accent rings; exact size, forward voltage, and quantity should be verified.

### Previously reported mechanical issues

- Cracks in head dome and chin, sun discoloration, and broken/immobile arm joints.
- Degraded rubber claws; replacements may be 3D-printed.
- Original wheel/gear mechanism is noisy/heavy; a tread-drive redesign has been explored.
- Neck geometry and motion limits require measured calibration.

## 3. Verified RGB eye electrical architecture

### Raspberry Pi 5 ↔ two SSD1351 displays

**BCM GPIO numbering** and **40-pin header physical pin numbers** are intentionally both shown.

| Signal | Eye 1: SPI5 CE0 | Eye 2: SPI5 CE1 |
| --- | --- | --- |
| 3.3V / VCC | Physical pin **1** | Physical pin **17** |
| Ground | Physical pin **6** | Physical pin **9** |
| DIN / MOSI | GPIO **14**, physical pin **8** | Shared GPIO **14**, physical pin **8** |
| CLK / SCLK | GPIO **15**, physical pin **10** | Shared GPIO **15**, physical pin **10** |
| CS | GPIO **12**, physical pin **32** | GPIO **26**, physical pin **37** |
| DC | GPIO **25**, physical pin **22** | GPIO **22**, physical pin **15** |
| RST | GPIO **24**, physical pin **18** | GPIO **23**, physical pin **16** |
| Linux device | `/dev/spidev5.0` | `/dev/spidev5.1` |

- Both OLED modules are configured for **4-wire SPI** (`BS=0`).
- DIN and CLK are shared through **two separate breadboard rows**; CS, DC, and RST remain independent.
- `/boot/firmware/config.txt` was configured with `dtparam=spi=on` and `dtoverlay=spi5-2cs`. **This boot configuration is not automatically tracked by the Git repository.** Verify it after OS changes or SD-card replacement.
- Python uses **`spidev` directly on bus 5**, plus **`lgpio`** for DC/RST and Pillow for drawing. Avoid switching back to default `board.SPI()` without confirming which SPI bus it selects.
- Working initial SPI speed: **8 MHz**, mode **0**.
- The ReSpeaker HAT's APA102 LEDs previously lit unexpectedly when displays were driven over SPI0; using SPI5 avoided that observed interference. This does **not** constitute a complete validation of microphone/HAT functionality.

### Power and electrical safety

- OLEDs are supplied from the Pi's **3.3V pins** as tested. Confirm total 3.3V rail budget before adding further devices.
- **Do not power motors, servos, or LED rings from GPIO pins.** Use appropriately rated power distribution, regulation, and switching circuits.
- Keep external servo power **off** during display-only troubleshooting.
- Confirm common-ground requirements and power-domain isolation for each controller/driver before connecting.
- The proposed white LED rings require **current limiting for each LED branch** and separate driver validation. Product marketing ratings (for example, a MOSFET's headline amperage) are not proof of safe GPIO input current or 5V switching behavior.

## 4. Software and repository state

### Repository layout (existing project)

The existing GitHub repository has directories including `backend/`, `frontend/`, `hardware/`, `software/eyes/`, and `system/`. **Use this structure; do not replace it with an unrelated new layout.**

### Verified RGB scripts

| Path in GitHub feature branch | Purpose |
| --- | --- |
| `software/eyes/rgb_eye_spi5_test.py` | Working standalone Eye 1 SPI5 CE0 test. |
| `software/eyes/rgb_eye2_test.py` | Working standalone Eye 2 SPI5 CE1 test. |
| `software/eyes/rgb_dual_eyes.py` | Dual-display synchronized gaze and blink animation. |
| `software/eyes/rgb_eye_test.py` | Earlier RGB test; inspect before reuse. |

The dual-eye script renders a soft off-white (`RGB 218,218,218`, `#DADADA`) eye field with black pupils. It demonstrates center, horizontal, vertical, and diagonal gaze targets, smoothstep motion interpolation, and simultaneous blink sequences. Both displays are updated sequentially on the shared SPI bus; frame timing and synchronization can be optimized later.

### Existing software to preserve

Older files include `diagonal_gaze.py`, `coordinated_gaze.py`, `autonomous_tomy.py`, `eye_behaviors.py`, and neck test/calibration scripts. They may contain useful Arduino communication and motion logic. **Review rather than overwrite** these files when integrating the neck.

### Git state as last confirmed

- Existing GitHub repository: `95toyotatacoma/tomy2000`.
- New branch pushed: **`feature/rgb-eyes`**.
- Feature commit: **`56823d2`** — `feat(eyes): add dual RGB OLED gaze and blinking animations`.
- Raspberry Pi's first local snapshot: **`e32b1e6`** — `feat: establish Tomy eye controls and RGB gaze animations`.
- Local backup branch: **`backup/rgb-eyes-working`**, pointing to the initial local snapshot; **not confirmed pushed** to GitHub.
- GitHub `main` and the feature branch have distinct purposes. **Do not assume the feature branch has been merged.**
- The earlier Pi working directory `~/tomy/eyes/` contains a Python virtual environment and possibly untracked local content; GitHub source files now live at `~/tomy/software/eyes/` when checked out on the feature branch. Check `git status`, the active branch, and the active virtual environment before running scripts.

## 5. Engineering decisions

| ID | Decision | Reason | Status |
| --- | --- | --- | --- |
| DEC-001 | Use SPI5 (`spi5-2cs`) for RGB eyes | Avoid observed SPI0 contention with ReSpeaker LEDs | **Implemented and tested** |
| DEC-002 | Use independent CS/DC/RST, shared MOSI/SCLK | Address two SSD1351 displays on one bus | **Implemented and tested** |
| DEC-003 | Preserve known-good individual eye test scripts | Easier regression testing and fault isolation | **Implemented** |
| DEC-004 | Develop gaze and blink before neck integration | Isolate display animation from servo/power issues | **Implemented for eyes; neck pending** |
| DEC-005 | Preserve GitHub's existing project layout | Avoid overwriting established software | **Implemented in feature branch** |
| DEC-006 | Use simple continuous white eye accent rings | OLEDs handle expression; ring supplies visual presence | **Design intent only** |
| DEC-007 | Investigate 3.3V-triggered MOSFET PWM modules for rings | Independent brightness control with external LED power | **Candidate selected; not electrically validated** |

## 6. Known issues, risks, and verification gaps

1. **Neck integration pending.** Existing Arduino servo commands, safe motion ranges, power distribution, and emergency stop behavior need confirmation before coordinated animation.
2. **SPI5 boot configuration not in source control.** Reproduce and document setup instructions; consider a configuration example rather than copying unrelated boot settings wholesale.
3. **Python environment portability.** Capture a tested dependency list and startup instructions for the RGB eye scripts. The existing root `requirements.txt` may not yet include every needed package.
4. **Eye module mapping.** Software calls devices Eye 1 (CE0) and Eye 2 (CE1); which is Tomy's physical left/right eye has not been recorded. Label them before adding asymmetric expressions.
5. **Physical wiring permanence.** Breadboard connections worked for testing; design strain relief, connectors, and a reliable harness for head motion.
6. **MOSFET ring circuit unverified.** Proposed AOD4184 optocoupler modules reportedly support 3.3V control, but input current, switching polarity, PWM behavior, load-side operation at 5V, and wiring require bench validation against the exact purchased board.
7. **Diffusion geometry untested.** LED count, ring diameter, optical cavity depth, PETG translucency, heat, and light uniformity require a prototype.
8. **No recent system-wide power-budget verification.** Establish measured rail loads and fusing before connecting additional LEDs, motors, and sensors.
9. **Git feature branch not merged.** Review/test from `software/eyes/`, then open a pull request when ready.

## 7. Next milestones

### Next engineering session: eyes + neck

1. Confirm current Git branch, working directory, Python environment, and RGB test operation from `software/eyes/`.
2. Identify physical **left/right** OLED assignments.
3. Inspect existing Arduino neck firmware and Python `diagonal_gaze.py` / `coordinated_gaze.py` interfaces.
4. Confirm servo power, safe pan/tilt ranges, calibration, and manual stop behavior.
5. Add a nonblocking or safely sequenced gaze-to-neck coordination layer without breaking standalone eye tests.
6. Bench-test eye and neck movement together at conservative motion limits.

### Separate lighting workstream: eye accent rings

1. Measure intended ring inner/outer diameters and available faceplate depth.
2. Prototype **one** short arc using existing white LEDs, correctly calculated current-limiting resistors, and a translucent 3D-printed diffuser.
3. Validate the exact 3.3V-control MOSFET module on the bench **before** connection to the Pi.
4. Choose LED count, spacing, power budget, and two-channel dimming approach based on measurements.
5. Build two continuous, softly illuminated white rings; reserve animated expressions for the RGB OLEDs.

## 8. Development log

### 2026-10-19 — Dual RGB eyes brought online

**Focus:** Replace earlier monochrome OLED experiments with two RGB SSD1351 displays and preserve progress in GitHub.

**Completed and verified:**
- Configured Raspberry Pi 5 SPI5 with two chip selects.
- Established both SSD1351 displays on shared MOSI/CLK and independent CS/DC/RST.
- Demonstrated individual display output with off-white background and black pupil.
- Verified ReSpeaker APA102 LEDs remained off during SPI5 display testing.
- Created and tested synchronized eight-direction gaze and blinking animation.
- Fixed a Pillow rectangle bounds error and a subsequent Python indentation error during testing.
- Initialized local Git history, fetched existing GitHub repository, preserved a backup branch, and integrated four RGB scripts into the existing `software/eyes/` structure.
- Committed feature as `56823d2` and pushed `feature/rgb-eyes` to GitHub.

**Not completed:** Neck synchronization, production wiring, full HAT audio verification, merging feature branch into `main`.

### 2026-10-20 — Eye accent lighting concept

**Focus:** Explore Watti-inspired continuous illuminated rings around Tomy's OLED eyes.

**Decisions / direction:**
- Prefer a **simple, steady white ring around each eye**; animations remain on RGB screens.
- Explore arrays of existing white through-hole LEDs behind translucent 3D-printed diffuser rings, rather than forcing straight COB strip into a tight flat circle.
- Consider independent PWM dimming for each ring using one 3.3V-compatible MOSFET module per eye.
- AOD4184 optocoupler MOSFET modules were identified as a **candidate**, based on seller/reviewer claims of 3.3V triggering; not yet bench-tested or confirmed installed.

**Next:** Prototype optical diffusion and validate driver electronics; no ring installation recorded.

## 9. Session handoff checklist

Before continuing work, check:

```bash
cd ~/tomy
git status --short
git branch --show-current
git log -1 --oneline
ls /dev/spidev*
```

Also verify `dtparam=spi=on` and `dtoverlay=spi5-2cs` in `/boot/firmware/config.txt` if displays stop responding. Confirm the servo power state before starting any test. Avoid running two scripts that claim the same GPIO lines simultaneously.

**Guiding principle:** Record demonstrated capabilities as **verified**, proposals as **planned**, and uncertain details as **needs verification**. Update this document after meaningful hardware, software, or architecture changes.
