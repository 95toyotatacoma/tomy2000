# TOMY — Security Architecture Decision Log

**Draft v0.1 | 2026-10-20**

Document decisions as **proposed**, **accepted**, **implemented**, or **verified**. A proposed rule is not evidence of protection.

| ID | Decision / proposal | Rationale | Status |
| --- | --- | --- | --- |
| SEC-ADR-001 | Safety and privacy controls take priority over character behavior | Align with TOMY Charter | **Charter principle; enforcement unverified** |
| SEC-ADR-002 | Separate Character/Behavior intent from hardware authorization | Prevent model/personality bypass of motion rules | Proposed |
| SEC-ADR-003 | Provide hardware-effective emergency stop and controller watchdog | Protect against Pi/software failures | Proposed |
| SEC-ADR-004 | Default to local, ephemeral sensing; opt-in persistence | Minimize privacy exposure | Proposed |
| SEC-ADR-005 | Default remote operation to disabled until authenticated controls exist | Reduce attack surface | Proposed |
| SEC-ADR-006 | Never place secrets in Git; audit history | Protect credentials | Proposed |

## Decision record template

```markdown
### SEC-ADR-XXX — Title
- Date:
- Status: Proposed / Accepted / Implemented / Verified / Superseded
- Context:
- Options considered:
- Decision:
- Safety / privacy impact:
- Validation evidence:
- Follow-up:
```
