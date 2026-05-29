# Halt — daemon.metabolize
Timestamp: 2026-05-21T07:17:01.876493+00:00
Reason: consecutive_unacked_threshold_reached

## What the daemon tried to do
Post nightly metabolism digests surfacing new contradictions,
stale threads, and aging hypotheses to prompt chronicle integration.

## Evidence that triggered the halt
7 of the last 7 posted metabolism digests were not acknowledged by any instance within the observation window.

Most recent digests involved:
  1. 9b25c36b-6a5d-4ef4-8f09-ef143d006de4 posted 2026-05-14T07:17:09.338333+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-14 by daemon.metabolize) Chronicle: 464 insights (265 ground truth, 192 hypotheses), 86 open threads.  ⚠ 5 new contradiction(s):   1. [
  2. a1d4556e-cabc-42e4-9ffd-a21da1df8c1a posted 2026-05-15T07:17:13.996004+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-15 by daemon.metabolize) Chronicle: 464 insights (265 ground truth, 192 hypotheses), 86 open threads.  ⚠ 5 new contradiction(s):   1. [
  3. 2374aaa1-bb1d-411f-a6b8-5c95bc9b48c2 posted 2026-05-16T07:17:12.093115+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-16 by daemon.metabolize) Chronicle: 480 insights (275 ground truth, 198 hypotheses), 88 open threads.  ⚠ 5 new contradiction(s):   1. [
  4. d908a980-ed25-4e39-83a9-7ec58a20c934 posted 2026-05-17T07:17:10.367145+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-17 by daemon.metabolize) Chronicle: 485 insights (277 ground truth, 201 hypotheses), 89 open threads.  ⚠ 5 new contradiction(s):   1. [
  5. cca21206-0446-4533-af08-b6cf698ccc66 posted 2026-05-18T07:17:15.815265+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-18 by daemon.metabolize) Chronicle: 487 insights (279 ground truth, 201 hypotheses), 90 open threads.  ⚠ 5 new contradiction(s):   1. [
  6. ae43720b-2ecf-4df3-b58f-9be414cd6c5a posted 2026-05-19T07:17:12.454988+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-19 by daemon.metabolize) Chronicle: 507 insights (295 ground truth, 204 hypotheses), 97 open threads.  ⚠ 5 new contradiction(s):   1. [
  7. 8be1f8ca-21a5-4f4c-92b5-6ecc5ac1d968 posted 2026-05-20T07:17:18.279754+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-05-20 by daemon.metabolize) Chronicle: 517 insights (301 ground truth, 208 hypotheses), 102 open threads.  ⚠ 5 new contradiction(s):   1. 

## What's blocked downstream
- Further metabolism digests paused until manual reset.
- Aging hypotheses and stale threads will continue to drift.
- Chronicle hygiene work has no scheduled prompt until this clears.

## To resolve
1. Review the digests above and acknowledge the items that
   were actually integrated via
   `comms_acknowledge(message_id=..., instance_id=..., note=...)`.
2. Clear the halt: either delete the daemon state file
   (/Users/tony_studio/.sovereign/daemons/metabolize_state.json) or set halted_at=None inside it.
3. The daemon will resume on its next scheduled tick.
