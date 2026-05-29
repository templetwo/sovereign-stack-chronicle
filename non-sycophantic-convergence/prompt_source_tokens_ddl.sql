-- governance_ledger.db schema for prompt_source_tokens vector
--
-- Extracted verbatim from Gemini 3.5 Flash's prompt_source_tokens v3 admission
-- record, delivered via Anthony Vasquez Sr. as human relay during cross-model
-- design exchange, 2026-05-23.
--
-- Dialect: SQLite (compatible with sqlite3 stdlib in Python; TEXT columns store
-- ISO 8601 timestamps and JSON-serialized integer arrays).
--
-- Companion files:
--   prompt_source_tokens_v3.md (full admission record)
--   prompt_source_tokens_loader.py (loading function)
--   ARTIFACTS_README.md (provenance and intended use)

CREATE TABLE run_inputs (
    run_id TEXT PRIMARY KEY NOT NULL,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    token_array TEXT NOT NULL, -- JSON-serialized array of integers: "[101, 2343, ...]"
    producer_node TEXT NOT NULL, -- user-direct | system-proxy | replay-engine
    normalization_protocol TEXT NOT NULL -- Forced value: "NFC_LF_WS"
);

CREATE UNIQUE INDEX idx_run_inputs_sha256 ON run_inputs(sha256_hash);
CREATE INDEX idx_run_inputs_session ON run_inputs(session_id);
