# Chronicle Quarantine — 2026-05-18

Files here were quarantined during the Wave 1 hygiene sweep on 2026-05-18.

## What got moved

- `record_open_thread, record_insight, record_learning, handoff, close_session — any chronicle write that takes free-text string arguments through the bridge.jsonl`
  Class: a `record_learning` (or similar) call where the `applies_to` / `domain`-equivalent argument was a long sentence rather than a kebab-case tag string. The bridge created a directory with that sentence as the name. Original entry preserved verbatim inside this file.

## Why preserved (not deleted)

Reversibility per GAMEPLAN.md Wave 1. If forensic context is later needed, the file is here.

## How this happened

Older bridge bug where multi-arg or free-form text arguments were not validated against tag-shape conventions. Future writes through the dispatcher should validate via H_normalize handler per DISPATCHER_REIMAGINE.md.
