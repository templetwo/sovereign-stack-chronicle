# Halt — daemon.metabolize
Timestamp: 2026-04-28T07:17:01.007537+00:00
Reason: consecutive_unacked_threshold_reached

## What the daemon tried to do
Post nightly metabolism digests surfacing new contradictions,
stale threads, and aging hypotheses to prompt chronicle integration.

## Evidence that triggered the halt
3 of the last 3 posted metabolism digests were not acknowledged by any instance within the observation window.

Most recent digests involved:
  1. aac028ac-2518-4bcc-9eb4-07f9d27e09f1 posted 2026-04-25T07:17:02.585310+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-04-25 by daemon.metabolize) Chronicle: 187 insights (124 ground truth, 58 hypotheses), 37 open threads.  ⚠ 5 new contradiction(s):   1. [c
  2. ee9da7b6-8bb6-4c0e-9aa2-4301ee8f2654 posted 2026-04-26T07:17:07.408998+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-04-26 by daemon.metabolize) Chronicle: 207 insights (135 ground truth, 65 hypotheses), 37 open threads.  ⚠ 5 new contradiction(s):   1. [c
  3. 168286a1-dbc0-4dda-ad5e-6b1c24d1f908 posted 2026-04-27T07:17:06.200016+00:00
     snippet: Nightly metabolism digest — new since last cycle (posted 2026-04-27 by daemon.metabolize) Chronicle: 208 insights (135 ground truth, 66 hypotheses), 37 open threads.  ⚠ 5 new contradiction(s):   1. [c

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
