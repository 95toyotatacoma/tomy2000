# TOMY — Security & Safety Test Plan

**Draft v0.1 | 2026-10-20 | All tests pending unless explicitly noted**

> **Safety warning:** Do not test failure conditions with an unsecured moving robot. For initial motor tests, isolate power, lift drive elements clear of the floor where appropriate, use conservative limits, and have a physical power cutoff within reach. Design and verify the cutoff before autonomous motion.

| Test | Objective | Acceptance criteria | State |
| --- | --- | --- | --- |
| SEC-001 | Inventory SSH accounts and listening services | Only approved accounts/services active | Pending |
| SEC-002 | Check repository for committed secrets | No active credentials or private keys in tracked history | Pending |
| SEC-003 | Verify GPIO ownership and bus separation | RGB eyes operate without ReSpeaker APA102 LED interference | **Partially demonstrated** (eyes only) |
| SEC-004 | Verify physical motor emergency stop | Actuation stops independently of character process | Pending |
| SEC-005 | Kill Pi control process during bounded motor test | Motor controller times out to safe state | Pending |
| SEC-006 | Disconnect Pi-to-Arduino command link | Motion ceases within specified safe timeout | Pending |
| SEC-007 | Invalid/out-of-range motor command | Rejected before actuation; hardware limits still enforced | Pending |
| SEC-008 | Power loss and reboot | No unintended automatic motor restart | Pending |
| SEC-009 | Privacy mute and sensing indication | Mute blocks collection; indicator matches actual sensing state | Pending |
| SEC-010 | Unauthorized guest attempts admin command | Denied and safely logged | Pending |
| SEC-011 | Malicious instruction in voice/transcript | Cannot invoke shell, firmware changes or privileged motion | Pending |
| SEC-012 | Restore backup and rollback software update | Recoverable without unsafe motor activation | Pending |

## Evidence template

```text
Test ID:
Date:
Hardware / software versions:
Power and safety setup:
Steps performed:
Observed result:
Pass / fail / blocked:
Evidence location (photo, log, commit):
Follow-up issue:
```

## Next safe test sequence

1. Read-only SSH and service inventory.
2. Review tracked Git files and history for secrets.
3. Design physical stop and controller watchdog **before** motor integration.
4. Validate stop, limits and failure states with isolated motor tests.
5. Only then consider supervised autonomous motion.
