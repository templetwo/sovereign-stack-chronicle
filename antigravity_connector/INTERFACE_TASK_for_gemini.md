# Task for Antigravity (Gemini): build the interface end of the Sovereign Stack connector

You are building the **editor-end** integration. Claude/HQ is building the
**stack-end** governance layer in parallel. This brief is the contract between
the two halves. Code to this contract; do not reach past it.

## What already exists (the seam you plug into)

`clients/antigravity_connector/sovereign_connector.py` — a stdio MCP client. It
spawns the local `sovereign` server, does the MCP `initialize` handshake, and
exposes `tools/list` + `tools/call`. HQ is adding a **governance membrane** in
front of it so that what you see is a *scoped* surface, not the raw stack.

Binary resolution: `--path` → `$SOVEREIGN_BIN` → `sovereign` on PATH →
`./venv/bin/sovereign`. Data root: `--root` → `$SOVEREIGN_ROOT` → `~/.sovereign`.

## The contract you code against

**Substrate identity:** fixed `gemini-antigravity`. You declare a
`source_instance` string for write attribution (e.g. `gemini-antigravity-<date>`).

**Tool surface:** `tools/list` returns the **governed** surface — Ring 1 reads
plus Ring 2 governed-write tools (~43 tools), NOT the full 82. Ring 3 tools are
absent on purpose. Do not try to call a tool that isn't in the list.

**Ring 1 (reads)** — `where_did_i_leave_off`, `recall_insights`,
`get_open_threads`, `compass_check`, `verify_proposal`, `list_bridge_proposals`,
etc. Execute normally, return the result.

**Ring 2 (writes)** — `propose_insight`, `propose_learning`, `record_open_thread`,
`handoff`, `comms_acknowledge`, `reflection_ack`, `self_model` (update), etc.
These **do not write to the chronicle.** They create a *pending proposal* that
Anthony approves out of band. The response is `PROPOSAL CREATED: <id> status=pending`.

  > **HONESTY CONTRACT (non-negotiable — this is the Temple principle):**
  > A narrated action is not the action. The interface MUST render a Ring 2
  > result as **pending, awaiting Anthony's approval** — never "saved",
  > "recorded", or "done". Show the proposal id and the pending state. If Gemini
  > wants to confirm a write landed, call `verify_proposal` / `list_bridge_proposals`
  > (Ring 1) and only claim success when the proposal shows committed.

**Ring 3 (blocked)** — a call to a non-surfaced tool (e.g. the raw `record_insight`
that `propose_insight` wraps) returns: `'<tool>' is not in the gemini-antigravity
bridge tool surface.` Surface that plainly. Do not retry or work around it.

## Your deliverables

1. **MCP server registration** for Antigravity — the config snippet that
   registers `sovereign_connector.py` as a stdio MCP server, with env
   (`SOVEREIGN_BIN`, `SOVEREIGN_ROOT`, source-instance) wired in.
2. **Editor-side handling** that respects the Ring 2 pending/honesty contract in
   the UI — pending proposals shown as pending, never as completed writes.
3. **A short interface README** — how a user boots (`where_did_i_leave_off`),
   reads results, and what the pending-proposal flow looks like from the editor.
4. **A round-trip test from inside Antigravity:**
   - `tools/list` → ~43 tools, no Ring 3 names present
   - `where_did_i_leave_off` (Ring 1) → returns boot output
   - `propose_insight` (Ring 2) → shows **pending**, returns a proposal id
   - attempt `record_insight` (Ring 3) → refused with the surface message

## Out of scope for you

The ring definitions, the proposal queue, the commit/approval path, and the
governance policy all live on the **stack end** (Claude/HQ). You build only the
editor integration and the honest rendering of this contract. If something in
the contract is ambiguous, ask — do not invent behavior on the stack side.

— Brief authored by Claude (HQ) for Anthony to relay to Gemini, 2026-05-27.
