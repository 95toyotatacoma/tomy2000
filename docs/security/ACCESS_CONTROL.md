# TOMY — Access Control and Command Authorization

**Draft v0.1 | 2026-10-20 | Proposed policy, not implemented**

## Roles

- **Owner/Maintainer:** installation, configuration, firmware updates, calibration, logs.
- **Trusted Operator:** approved interactions and bounded motion controls.
- **Guest:** ordinary conversation and nonhazardous interactions.
- **Autonomous Character:** selects from approved, context-limited actions.
- **External Service:** restricted to explicitly authorized APIs, if ever enabled.

## Command classes

| Class | Examples | Proposed authorization |
| --- | --- | --- |
| Emergency | Stop motion, disable motor power | Accessible immediately; physical stop independent of login |
| Privacy | Mute microphones, stop recording, clear session | Accessible to affected users; deletion scope needs design |
| Low risk | Eye animations, harmless sounds | Character, operator, guest as context permits |
| Motion | Neck/arm movement, driving | Trusted operator or bounded autonomous policy after safety validation |
| Administrative | Update software, calibrate limits, modify permissions | Owner only; authenticated and logged |
| Sensitive data | Export transcripts, memories, credentials | Owner-controlled; consent and data minimization required |

## Required checks before action

1. Is the command type recognized and structurally valid?
2. Is the actor authorized for this command and current operating mode?
3. Is a privacy or emergency-stop state active?
4. Are all limits, environmental conditions and required sensor readings valid and fresh?
5. Does the low-level controller independently enforce duration and motion bounds?
6. Can the action be interrupted promptly?

**Deny by default** when authorization or safety state is unknown. Never interpret a model-generated sentence as proof of authority. Tomy's stubborn dialogue may occur **after** compliance with stop/privacy commands, not before.

## Open design decisions

- Owner identity and local authentication method.
- Guest interaction policy and whether speaker recognition is appropriate.
- Remote operation policy (default recommendation: disabled).
- Trusted operator enrollment and revocation.
- Audit event schema, access and retention.
