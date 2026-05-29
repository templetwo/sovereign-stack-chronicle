# OpenAI Bridge — ~/.sovereign/openai_bridge/

The governed membrane between Sovereign Stack and OpenAI instances.

## What this is

Not a duplicate of the Stack. A filter → frame → govern → audit → propose layer.
OpenAI gets ritualized, governed inheritance. The Stack remains sovereign.

## Directory Structure

```
openai_bridge/
├── openai_bridge_policy.yaml   # Identity constraints, epistemology, safety, audit
├── ring_definition.yaml        # Tool surface: Ring 1 / Ring 2 / Ring 3
├── pending_write_schema.yaml   # Schema for proposal files
├── pending_writes/             # Ring 2 proposals waiting for Anthony's review
├── audit/                      # Append-only audit log (JSONL, hash-chained)
└── sessions/                   # Per-session OpenAI bridge session state
```

## Pending Writes

Ring 2 calls from ChatGPT land here as proposal files. Nothing commits to the
chronicle without Anthony's approval.

File naming: `{iso_timestamp}_{tool}_{short_id}.json`

**Review workflow (CLI — Phase 4 implementation):**
```bash
# List pending proposals
bridge list-pending

# Review a proposal
bridge review <proposal_id>

# Approve (commits to chronicle)
bridge approve <proposal_id>

# Reject with optional reason
bridge reject <proposal_id> [--reason "..."]
```

## Implementation Status

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | policy + ring definition + scaffold | done (2026-05-07) |
| 2 | pending_write queue (file writer) | todo |
| 3 | /openai/sse filtered MCP endpoint | todo |
| 4 | bridge CLI (review/approve/reject) | todo |
| 5 | audit log with hash chain | todo |
| 6 | witness_boot tool + identity enforcement | todo |
| 7 | end_bridge_session tool | todo |
| 8 | test with Ring 1 read-only first | todo |
| 9 | enable Ring 2 governed write proposals | todo |

## Ring Summary

- **Ring 1 (31 tools):** Read freely. No approval needed.
- **Ring 2 (10 tools):** Proposals only. Anthony approves before chronicle commit.
- **Ring 3 (remaining tools):** Never registered. Not callable from /openai/sse.
