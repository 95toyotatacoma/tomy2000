# TOMY — Security Architecture

**Proctor House Studio | Draft v0.1 | 2026-10-20**  
**Status:** Proposed architecture; **not** a claim of implemented protections.  
**Companion documents:** `docs/TOMY_CHARTER.md`, `docs/engineering/ENGINEERING_STATE.md` (adjust links to actual repository locations).

## 1. Purpose and governing principles

Tomy is an embodied robotic character, not a general-purpose assistant. Security must protect people, their privacy, Tomy's physical systems, and the integrity of his character without making safe playfulness impossible.

The Charter establishes that Tomy's personality cannot override safety, privacy, or human-directed interruption; the proposed Safety Supervisor must be able to inhibit unsafe actions independently of the Character and Behavior Engines. The Engineering State confirms working RGB eyes and SPI5, while neck, drive, microphone functionality, and other subsystems remain in varying stages of development.

**Nonnegotiable rules:**
1. **Safety before character.** An emergency stop or privacy control executes immediately; Tomy may comment afterward, never delay it.
2. **Least privilege.** Components and users receive only the permissions they need.
3. **Fail safe.** Missing heartbeat, lost communication, unsafe power, or invalid sensor data must not result in uncontrolled movement.
4. **Local-first privacy.** Prefer local processing; minimize retention and external transmission.
5. **Explicit authorization.** Autonomous actions stay within approved spaces, capabilities, and operating modes.
6. **Verifiable boundaries.** A software promise is not a hardware safety mechanism; test safeguards before enabling autonomous motion.
7. **No secret values in Git.** Document configuration patterns, never credentials.

## 2. Scope and current security posture

| Area | Current evidence | Security status |
| --- | --- | --- |
| Raspberry Pi 5 | Operational for SPI5 OLED tests | OS hardening, users, SSH and firewall **not audited** |
| RGB eye displays | Dual gaze and blinking verified | Low physical risk; GPIO ownership and process isolation need review |
| ReSpeaker microphone HAT | Installed/reported; SPI0 LED contention observed | Recording, permission, retention and mute controls **not implemented/verified** |
| Arduino neck servos | Earlier prototypes; integration pending | Limits, watchdog and physical stop **require validation** |
| Drive motors / treads | In development | No autonomous movement authorization |
| Sensors, cameras, network services | Various planned or reported | Inventory, permissions and data flows **unverified** |
| GitHub | Feature branch with eye code pushed | Repository access, branch protection and secret scanning **not audited** |

**Release gate:** Until motion safeguards are physically tested, restrict development to supervised bench tests with servo/motor power controlled separately. Do not enable unattended locomotion.

## 3. Assets, actors, and trust boundaries

**Protect:** people and pets nearby; motors, battery and electronics; microphone/visual/interaction data; SSH credentials and API tokens; firmware, source code and personality settings; update integrity.

**Actors:** owner/maintainer; invited user; nearby bystander; Tomy's autonomous software; external cloud service (future); unauthorized local or network actor.

**Trust boundaries:**

```text
Nearby people / environment
      | sensors, microphone (untrusted inputs)
      v
[Perception] ---> [Character / Behavior engines] ---> [Policy + Safety Supervisor]
                                                         |
                                      approved bounded action only
                                                         v
                                               [Hardware control]
                                                         |
                                            [Arduino / motors / eyes]

Owner/admin --authenticated management--> Raspberry Pi / configuration
External services (optional) <--explicitly approved gateway--> Pi

HARDWARE MOTOR POWER DISABLE / E-STOP: independent of personality and
preferably effective even if Pi software hangs.
```

Sensor readings, speech transcripts, model-generated instructions, and downloaded content are **data**, never inherently authorized commands. Hardware-control APIs must validate requests independently.

## 4. Identity, roles, and authorization (target)

| Role | Permitted actions (proposed) | Not permitted |
| --- | --- | --- |
| Owner / maintainer | Provision, update, calibrate, review logs, enable supervised test modes | Bypass physical emergency stop |
| Trusted operator | Start/stop approved behaviors within configured limits | Modify safety limits or credentials |
| Guest / bystander | Basic interaction, request quiet/privacy mode, stop movement | Admin access, access to retained private data |
| Autonomous character | Choose from pre-approved behaviors within active mode | Alter safety rules, self-grant permissions, deploy code, access secrets |
| Remote service | Only narrowly scoped approved functions | Direct unrestricted motor or shell access |

**Design decisions to make:** local identity method, guest recognition, whether remote access is needed, and whether all users can issue stop commands (recommended: yes, without authentication for a physical stop).

## 5. Safety-critical command path

**Target command pipeline:** intent -> authorization -> context/safety checks -> bounded action -> low-level controller -> monitored execution.

For every motorized subsystem define and test: position/speed/current limits, forbidden zones, obstacle response, startup state, watchdog timeout, communication-loss behavior, low-battery behavior, and an accessible power-cut stop. Software stop is useful but not sufficient by itself for a moving robot.

**Emergency-stop behavior (target):**
- Immediately disable motor actuation; do not wait for dialogue or character logic.
- Require deliberate operator reset after a latched emergency stop.
- Never automatically resume movement after power restoration or network reconnection.
- Log the stop reason without storing unnecessary personal data.

**Current status:** no verified end-to-end E-stop, watchdog, or motor interlock recorded. Treat this section as requirements, not existing protections.

## 6. Privacy and data handling

**Default policy proposal:** no persistent raw audio/video recording; process locally where practical; make sensing state visible; obtain explicit permission before retaining or transmitting identifiable recordings. Support an accessible microphone mute and clear data deletion controls. Define retention windows per data class before enabling memory features.

| Data class | Default target | Retention decision |
| --- | --- | --- |
| Distance/light/IMU readings | Ephemeral local processing | No retention unless needed for diagnostics |
| Raw microphone audio | Transient processing only | Recording disabled by default |
| Speech transcripts | Ephemeral unless opted in | Define retention and deletion before rollout |
| Preferences/character memory | Minimal, user-reviewable | Define opt-in, expiry and deletion |
| Diagnostic logs | Redacted technical events | Define rotation and retention |
| Camera/visual data (future) | Disabled until privacy design reviewed | No storage by default |

A microphone HAT being installed does **not** mean a privacy control is implemented.

## 7. Platform and network hardening (planned checklist)

- Inventory OS version, services, listening ports, accounts and connected devices.
- Use unique credentials; SSH keys; disable password-based SSH only **after** confirming working key access.
- Restrict administrative privileges; run robot services under dedicated low-privilege accounts where feasible.
- Keep system packages and dependencies patched with a tested rollback plan.
- Disable unnecessary services and network exposure; segment untrusted IoT devices if relevant.
- Protect secrets outside source control; audit tracked history before publishing.
- Pin/verify dependencies and review changes before installing untrusted code.
- Keep backups of configuration and recovery instructions; avoid committing machine-specific secrets.
- Define secure remote update and rollback procedures before remote administration is enabled.

## 8. Software isolation and AI/character boundaries

- Character/Behavior engines emit **intent**, never raw GPIO commands or shell commands.
- A policy layer validates action type, target, authorization, mode, duration, and numeric bounds.
- Hardware drivers accept only structured, validated requests.
- Treat spoken commands, external text, and AI outputs as untrusted; do not allow them to rewrite policy, access credentials, or execute arbitrary code.
- Keep emergency stop and privacy controls outside the model's discretion.
- Log rejected unsafe requests at an appropriate, privacy-preserving level.
- Autonomous learning may adjust preferences, but **must not** modify safety-critical rules or firmware.

## 9. Security verification and release gates

| Gate | Required evidence | State |
| --- | --- | --- |
| S-01 | GPIO and electrical map checked for conflicts | **Partial**: eye SPI5 map documented |
| S-02 | Motor power disable/E-stop physically tested | **Not verified** |
| S-03 | Servo/drive limits and communication-loss stop tested | **Not verified** |
| S-04 | SSH users, ports, permissions and update process reviewed | **Not audited** |
| S-05 | Audio sensing indicator, mute and recording policy tested | **Not verified** |
| S-06 | Character requests cannot bypass action policy | **Not implemented/verified** |
| S-07 | Credentials excluded from repository and history checked | **Not audited** |
| S-08 | Recovery from crash/reboot/low battery safely tested | **Not verified** |

## 10. Threats and mitigations

See [THREAT_MODEL.md](THREAT_MODEL.md) for scenarios and prioritization, [ACCESS_CONTROL.md](ACCESS_CONTROL.md) for role and command policy, and [SECURITY_TEST_PLAN.md](SECURITY_TEST_PLAN.md) for repeatable validation.

## 11. Decisions awaiting owner approval

1. Will Tomy ever be accessible from outside the home network?
2. Who should be allowed to operate or calibrate motors?
3. What physical emergency-stop switch and motor power isolation will be used?
4. Will microphone processing be fully local, hybrid, or cloud-backed?
5. Should Tomy store conversations, and if so, what consent and deletion controls are required?
6. What is the minimum safe behavior when perception, network, or control communication fails?

## 12. Maintenance

Update after every meaningful architecture or safety decision. Distinguish **verified**, **reported**, **planned**, and **needs verification**. Record implementation evidence in `ENGINEERING_STATE.md`; log security decisions in `SECURITY_DECISIONS.md`.
