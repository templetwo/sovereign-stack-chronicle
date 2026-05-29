# Cross-Model Artifacts: Non-Sycophantic Convergence Protocol

**Provenance:** These files are verbatim extractions from Gemini 3.5 Flash outputs, relayed by Anthony Vasquez Sr. as human carrier between Gemini, ChatGPT (OpenAI seat, partially blind due to OAuth bridge regression), and web-chat Claude (Opus 4.7) during a multi-hour cross-model design session on 2026-05-23.

**Why these exist as separate files:** HQ-Opus 4.7 correctly identified that the handoff document (`non-sycophantic-convergence_build-handoff.md`) treated "design phase closed, build phase opens" as if the verbatim artifacts were on disk. They were not. They existed only in the cross-model chat transcripts. Without the verbatim on disk, Tier 2 verification work (running the Python loader, validating the DDL, etc.) would be verification-of-reconstruction, not verification-of-artifact. That is the adversary-design problem one layer down.

**These files contain known issues that should NOT be cleaned up before verification work:**

The Python in `chronicle_failure_profile_loader.py` contains three issues identified during the design exchange but deliberately left as-delivered:
1. Missing `import unicodedata` at the top of the function (probably implicit, but not declared)
2. Noop `encode("utf-8")` followed immediately by `.decode("utf-8")` before `unicodedata.normalize` (the roundtrip accomplishes nothing)
3. NFC normalization ordered AFTER whitespace and line-ending operations (canonically should be FIRST, since NFC can produce character-width changes that affect whitespace handling)

These bugs are the test material for Tier 2 verification. If the file with the bugs intact reproduces the bugs when run, the exchange's identification of them is verified. If running the file reveals additional bugs not previously identified, that is new signal worth chronicling.

**File listing:**

| File | Source | Purpose |
|---|---|---|
| `prompt_source_tokens_v3.md` | Gemini v3 delivery, verbatim | Full admission record, simpler bounded-input vector |
| `chronicle_failure_profile_v2.md` | Gemini v2 delivery, verbatim | Full admission record, complex multi-document vector |
| `prompt_source_tokens_loader.py` | Extracted from v3 record | Standalone Python: `fetch_prompt_source_tokens` |
| `prompt_source_tokens_ddl.sql` | Extracted from v3 record | Standalone SQL: `governance_ledger.db` schema |
| `chronicle_failure_profile_loader.py` | Extracted from v2 record | Standalone Python: `deterministic_load_chronicle_state` (with the three bugs preserved) |
| `chronicle_failure_profile_ddl.sql` | Extracted from v2 record | Standalone SQL: `chronicle_failure_profiles_v2` schema (PostgreSQL-style with `gen_random_uuid()`, `JSONB`, `TIMESTAMP WITH TIME ZONE`) |

**Suggested next actions for HQ-Opus 4.7:**

1. Read each `.md` file in full to confirm the artifacts match what the chronicle summarized.
2. Create a sandbox environment (a `/tmp/non-sycophantic-convergence-verify/` directory or similar) and run the SQL DDLs against actual database engines. The prompt_source_tokens DDL is SQLite-flavored; the chronicle_failure_profile DDL is PostgreSQL-flavored (uses `JSONB`, `gen_random_uuid()`, `TIMESTAMP WITH TIME ZONE`). Pick the matching engine per file.
3. Run `chronicle_failure_profile_loader.py` against synthetic test data to confirm the three identified bugs reproduce.
4. Optionally compare what running the code reveals against what the chronicle entries for `v2-provisional-acceptance` claim. Any divergence is signal for the format-divergence methodology finding (which currently has two data points; this would add a third or a counterexample).

**Provenance audit trail:**

These artifacts came through a chain: Gemini 3.5 Flash → Anthony's ChatGPT/Gemini browser session → copy-paste into web-chat Claude conversation as document uploads → web-chat Claude extracts to files → Anthony brings files to HQ. Each link in the chain is a potential corruption point. The integrity check is: do these files match what Anthony has in his Gemini conversation history? If they do, the chain is clean. If they don't, the divergence point is identifiable.

**Companion documents:**

- `non-sycophantic-convergence_build-handoff.md` (the lay-of-the-land handoff that preceded these files; read first)
- Sovereign Stack chronicle entries under master tag `non-sycophantic-convergence` (retrievable via `recall_insights({"domain_filter": "non-sycophantic-convergence", "limit": 20})`)
- Open threads under same master tag (retrievable via `get_open_threads`)

**Author:** Web-chat Claude (Opus 4.7), 2026-05-23
**Note:** Internal chronicle entries reference "2026-05-21" as the session date in their content body; actual session date and write timestamps are 2026-05-23. Author error, not chronicle corruption.
