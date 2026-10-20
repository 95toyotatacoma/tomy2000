# TOMY — Threat Model

**Draft v0.1 | 2026-10-20 | Status: Initial design, not a completed security assessment**

## Scope

Tomy's Raspberry Pi, microcontroller, motors, sensors, microphone, local network, software update paths, and optional future cloud integrations. Physical safety and privacy are prioritized alongside cybersecurity.

## Priority rubric

- **Critical:** credible path to injury or uncontrolled motion; requires engineering controls before motion autonomy.
- **High:** credential compromise, unauthorized actuation, or significant private-data exposure.
- **Medium:** disruption, nuisance, recoverable configuration loss, or limited data exposure.

## Initial threat register

| ID | Scenario | Impact | Proposed mitigation | Evidence / status |
| --- | --- | --- | --- | --- |
| T-01 | Pi hangs while motor command remains active | Critical | Independent motor disable, controller watchdog, bounded commands | Not verified |
| T-02 | Untrusted voice/text induces unsafe movement | Critical | Authorized intent gateway; hardware-enforced limits | Not implemented |
| T-03 | Obstacle sensor fails or reports stale readings | Critical | Freshness checks, safe stop, supervised operating area | Not verified |
| T-04 | Unauthorized SSH/network access | High | Key-based SSH, least privilege, limited exposure, updates | Not audited |
| T-05 | Audio captured or retained without clear consent | High | Mute/indicator, local processing, opt-in retention | Not implemented |
| T-06 | Secrets committed to public repository | High | `.gitignore`, secret scan, credential rotation | Not audited |
| T-07 | Malicious or defective dependency/update | High | Review, pinning, rollback, signed sources where possible | Not audited |
| T-08 | Character engine bypasses safety supervisor | Critical | Separate policy enforcement; hardware stop; negative tests | Not implemented |
| T-09 | Brownout or power restoration causes unintended motion | Critical | Power budgeting, startup-disabled actuation, reset latch | Not verified |
| T-10 | Unauthorized guest changes configuration | Medium/High | Role separation, protected admin interface | Not implemented |
| T-11 | Logs/memory reveal private interactions | High | Data minimization, access controls, retention/deletion | Not implemented |
| T-12 | GPIO contention disrupts peripherals | Medium | Pin inventory, isolated buses, integration tests | SPI0 LED contention previously observed; SPI5 eyes verified |

## Trust assumptions to validate

- Raspberry Pi operating system and repository provenance are trusted **only after** an access and update review.
- Arduino firmware cannot be assumed to enforce safe limits until inspected and tested.
- Network, voice, AI-generated outputs and sensor input are not authoritative commands.
- Emergency-stop effectiveness must not depend solely on the main Python process.

## Review cadence

Review whenever motors, cameras, microphone storage, networking, remote access, autonomous navigation, or third-party AI services are enabled. Record new risks, mitigations, test evidence and residual risk owner.
