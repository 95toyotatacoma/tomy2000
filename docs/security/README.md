# TOMY — Security Documentation

**Status: Architecture scaffold, 2026-10-20. No security controls are claimed implemented unless accompanied by test evidence.**

This directory extends the existing `TOMY_CHARTER.md` and `ENGINEERING_STATE.md`; it does not replace them.

| Document | Purpose |
| --- | --- |
| [SECURITY_ARCHITECTURE.md](SECURITY_ARCHITECTURE.md) | Principles, system boundaries, privacy, physical safety, and requirements |
| [THREAT_MODEL.md](THREAT_MODEL.md) | Initial threats, risks, and proposed mitigations |
| [ACCESS_CONTROL.md](ACCESS_CONTROL.md) | Roles, command classes, and authorization policy |
| [SECURITY_TEST_PLAN.md](SECURITY_TEST_PLAN.md) | Safety/security verification gates and evidence template |
| [SECURITY_DECISIONS.md](SECURITY_DECISIONS.md) | Proposed/approved architecture decisions and rationale |

## Integration

Suggested repository path: `docs/security/`. Keep the two existing documents in their current locations until their paths are deliberately standardized. Link to them from this directory once paths are confirmed.

**First implementation priority:** before neck/drive autonomy, design and validate independent motor stopping, command limits, watchdog behavior, and safe restart. Initial OS and repository security review can proceed without powering motors.
